# blog/urls.py
from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    # HOMEPAGE — Beautiful modern page with hero, featured, latest posts
    path('', views.post_list, name='home'),
    
    # FULL BLOG LIST — Optional separate page (e.g. /blog/)
    path('blog/', views.post_list, name='post_list'),

    # Post detail & actions
    path('post/<slug:slug>/', views.post_detail, name='post_detail'),
    path('post/<slug:slug>/like/', views.post_like, name='post_like'),
    path('post/<slug:slug>/comment/', views.add_comment, name='add_comment'),

    # Categories & Tags
    path('categories/', views.category_list, name='category_list'),
    path('category/<slug:slug>/', views.category_posts, name='category_posts'),
    path('tag/<slug:slug>/', views.tag_posts, name='tag_posts'),
    
    # Author page
    path('author/<str:username>/', views.author_posts, name='author_posts'),
    
    # Newsletter
    path('newsletter/subscribe/', views.newsletter_subscribe, name='newsletter_subscribe'),
]