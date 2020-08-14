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
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.contrib.postgres.search import TrigramSimilarity

def post_list(request, tag_slug=None):
    object_list = Post.published.all()
    t=Post.tags.all()
    tag = None

    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        print('tag',tag)
        object_list = object_list.filter(tags__in=[tag])
        print('obj',object_list)


    paginator = Paginator(object_list, 2) 
    page = request.GET.get('page',1)
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
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

    comments = post.comments.filter(active=True)

    new_comment = None

    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST or None)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.save()
            return redirect(post)
    else:
        comment_form = CommentForm()
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
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False

    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} recommends you read {post.title}"
            message = f"Read {post.title} at {post_url}\n\n" \
                      f"{cd['name']}\'s comments: {cd['comments']}"
            send_mail(subject, message, 'userr@gmail.com',
                      [cd['to']], fail_silently=True)
            sent = True

    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post': post,
                                                    'form': form,
                                                    'sent': sent})


def post_search(request):
    form = SearchForm()
    query = None
    result=[]
    if 'query' in request.GET:
        form=SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            search_vector = SearchVector('title', 'body')
            search_query = SearchQuery(query)
            result = Post.published.annotate(
                similarity=TrigramSimilarity('title', query),
            ).filter(similarity__gt=0.1).order_by('-similarity')
                        
    return render(request, 'blog/post/search.html', {'form': form, 'query': query, 'results': result})


