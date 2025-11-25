from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Post, Category, Tag, Comment, Newsletter
from datetime import datetime

def post_list(request):
    posts = Post.objects.filter(status='published').select_related('author', 'category').prefetch_related('tags')
    
    # Search
    query = request.GET.get('q')
    if query:
        posts = posts.filter(
            Q(title__icontains=query) |
            Q(excerpt__icontains=query) |
            Q(content_html__icontains=query) |
            Q(content_markdown__icontains=query)
        )
    
    # Featured posts
    featured_posts = posts.filter(is_featured=True)[:3]
    
    # Pagination
    paginator = Paginator(posts, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Popular posts
    popular_posts = Post.objects.filter(status='published').order_by('-views')[:5]
    
    # Categories with post count
    categories = Category.objects.annotate(num_posts=Count('posts', filter=Q(posts__status='published')))
    
    # Popular tags
    tags = Tag.objects.annotate(num_posts=Count('posts', filter=Q(posts__status='published'))).order_by('-num_posts')[:10]
    
    context = {
        'posts': page_obj,
        'featured_posts': featured_posts,
        'popular_posts': popular_posts,
        'categories': categories,
        'tags': tags,
        'query': query,
    }
    return render(request, 'blog/post_list.html', context)

def post_detail(request, slug):
    post = get_object_or_404(Post.objects.select_related('author', 'category').prefetch_related('tags'), slug=slug, status='published')
    
    # Increment views
    post.views += 1
    post.save(update_fields=['views'])
    
    # Comments
    comments = post.comments.filter(is_approved=True, parent=None).select_related('author')
    
    # Related posts
    related_posts = Post.objects.filter(
        status='published',
        category=post.category
    ).exclude(id=post.id)[:3]
    
    # Check if user liked
    user_liked = False
    if request.user.is_authenticated:
        user_liked = post.likes.filter(id=request.user.id).exists()
    
    context = {
        'post': post,
        'comments': comments,
        'related_posts': related_posts,
        'user_liked': user_liked,
    }
    return render(request, 'blog/post_detail.html', context)

def category_list(request):
    categories = Category.objects.annotate(
        num_posts=Count('posts', filter=Q(posts__status='published'))
    ).order_by('-num_posts')
    
    context = {
        'categories': categories,
    }
    return render(request, 'blog/category_list.html', context)

def category_posts(request, slug):
    category = get_object_or_404(Category, slug=slug)
    posts = Post.objects.filter(status='published', category=category).select_related('author')
    
    paginator = Paginator(posts, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'posts': page_obj,
    }
    return render(request, 'blog/category_posts.html', context)

def tag_posts(request, slug):
    tag = get_object_or_404(Tag, slug=slug)
    posts = Post.objects.filter(status='published', tags=tag).select_related('author', 'category')
    
    paginator = Paginator(posts, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'tag': tag,
        'posts': page_obj,
    }
    return render(request, 'blog/tag_posts.html', context)

@login_required
@require_POST
def post_like(request, slug):
    post = get_object_or_404(Post, slug=slug)
    
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True
    
    return JsonResponse({
        'liked': liked,
        'like_count': post.like_count()
    })

@login_required
@require_POST
def add_comment(request, slug):
    post = get_object_or_404(Post, slug=slug)
    content = request.POST.get('content')
    parent_id = request.POST.get('parent_id')
    
    if content:
        comment = Comment.objects.create(
            post=post,
            author=request.user,
            content=content,
            parent_id=parent_id if parent_id else None
        )
        return JsonResponse({
            'success': True,
            'comment': {
                'author': comment.author.get_full_name(),
                'content': comment.content,
                'created_at': comment.created_at.strftime('%B %d, %Y at %I:%M %p'),
            }
        })
    
    return JsonResponse({'success': False}, status=400)

@require_POST
def newsletter_subscribe(request):
    email = request.POST.get('email')
    
    if email:
        newsletter, created = Newsletter.objects.get_or_create(email=email)
        if created:
            return JsonResponse({'success': True, 'message': 'Successfully subscribed!'})
        else:
            if newsletter.is_active:
                return JsonResponse({'success': False, 'message': 'Email already subscribed!'})
            else:
                newsletter.is_active = True
                newsletter.save()
                return JsonResponse({'success': True, 'message': 'Subscription reactivated!'})
    
    return JsonResponse({'success': False, 'message': 'Invalid email!'}, status=400)

def author_posts(request, username):
    from users.models import CustomUser
    author = get_object_or_404(CustomUser, username=username)
    posts = Post.objects.filter(status='published', author=author).select_related('category')
    
    paginator = Paginator(posts, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'author': author,
        'posts': page_obj,
    }
    return render(request, 'blog/author_posts.html', context)