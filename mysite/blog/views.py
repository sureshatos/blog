from django.db.models import Count
from django.core.mail import send_mail
from django.shortcuts import render, get_object_or_404, HttpResponseRedirect, redirect
from django.core.paginator import Paginator, EmptyPage,\
    PageNotAnInteger
from django.views.generic import ListView
from .models import Post,User
from .forms import *
from django.contrib import messages
from taggit.models import Tag


def post_list(request, tag_slug=None):
    object_list = Post.published.all()
    t=Post.tags.all()
    tag = None


    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        print('tag',tag)
        object_list = object_list.filter(tags__in=[tag])
        print('obj',object_list)


    paginator = Paginator(object_list, 2)  # 3 posts in each page
    page = request.GET.get('page',1)
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer deliver the first page
        posts = paginator.page(1)
    except EmptyPage:
        # If page is out of range deliver last page of results
        posts = paginator.page(paginator.num_pages)
    return render(request,
                  'blog/post/list.html',
                  {'page': page,
                   'posts': posts, 't': t, 'tag': tag })


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post,
                             status='published',
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)
    
    # List of active comments for this post
    comments = post.comments.filter(active=True)

    new_comment = None

    if request.method == 'POST':
        # A comment was posted
        comment_form = CommentForm(data=request.POST or None)
        if comment_form.is_valid():
            # Create Comment object but don't save to database yet
            new_comment = comment_form.save(commit=False)
            # Assign the current post to the comment
            new_comment.post = post
            # Save the comment to the database
            new_comment.save()
            
            return redirect(post)
    else:
        comment_form = CommentForm()
    
     # List of similar posts
    post_tags_ids = post.tags.values_list('id', flat=True)
    print('post_tags_ids', post_tags_ids)
    print('post id',post.id)
    similar_posts = Post.published.filter(tags__in=post_tags_ids)\
                                  .exclude(id=post.id)
    print('similar_posts',similar_posts)
    similar_posts = similar_posts.annotate(same_tags=Count('tags'))\
        .order_by('-same_tags', '-publish')[:4]
    print('similar_posts 2', similar_posts)


    return render(request,
                  'blog/post/detail.html',
                  {'post': post,
                   'comments': comments,
                   'new_comment': new_comment,
                   'comment_form': comment_form, 'similar_posts': similar_posts
                   })




class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 2
    template_name = 'blog/post/list2.html'


def post_share(request, post_id):
    # Retrieve post by id
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False

    if request.method == 'POST':
        # Form was submitted
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # Form fields passed validation
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} recommends you read {post.title}"
            message = f"Read {post.title} at {post_url}\n\n" \
                      f"{cd['name']}\'s comments: {cd['comments']}"
            send_mail(subject, message, 'suresh.kadari2@gmail.com',
                      [cd['to']], fail_silently=True)
            sent = True

    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post': post,
                                                    'form': form,
                                                    'sent': sent})
