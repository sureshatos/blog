from django.contrib import admin
from django.urls import path, include
from blog.sitemaps import PostSitemap
from django.contrib.sitemaps.views import sitemap
from django.conf import settings
from django.conf.urls.static import static



sitemaps = {
    'posts': PostSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('blog/', include('blog.urls', namespace='blog')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps},
         name='django.contrib.sitemaps.views.sitemap')
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
