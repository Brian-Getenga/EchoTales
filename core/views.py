from django.shortcuts import render
from blog.models import Post, Category
from django.db.models import Count, Q

def home(request):
    # Featured posts (highlighted on hero section)
    featured_posts = (
        Post.objects.filter(status='published', is_featured=True)
        .select_related('author', 'category')
        .prefetch_related('tags')
        .order_by('-published_at', '-created_at')[:3]
    )

    # Latest posts (displayed under "Latest Posts" section)
    posts = (
        Post.objects.filter(status='published')
        .select_related('author', 'category')
        .prefetch_related('tags')
        .order_by('-published_at', '-created_at')[:12]
    )

    # Categories (displayed under "Explore Topics")
    categories = (
        Category.objects.annotate(
            num_posts=Count('posts', filter=Q(posts__status='published'))
        )
        .order_by('-num_posts', 'name')[:6]
    )

    context = {
        'featured_posts': featured_posts,
        'posts': posts,                # <- matches {% for post in posts|slice:":12" %}
        'categories': categories,      # <- matches {% for category in categories %}
    }
    return render(request, 'core/home.html', context)


def about(request):
    return render(request, 'core/about.html')

def contact(request):
    if request.method == 'POST':
        # Handle contact form submission
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        # You can add email sending logic here
        from django.contrib import messages
        messages.success(request, 'Your message has been sent successfully!')
    
    return render(request, 'core/contact.html')