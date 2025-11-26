from django.shortcuts import render
from blog.models import Post, Category
from django.db.models import Count, Q
# core/views.py
from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.db.models import Count  # ← THIS WAS MISSING
from blog.models import Post, Category

User = get_user_model()

def about(request):
    published_posts = Post.objects.filter(status='published')

    # Top 6 authors with most published posts
    top_authors = (User.objects
                   .filter(posts__status='published')
                   .annotate(post_count=Count('posts'))
                   .order_by('-post_count')[:6])

    context = {
        'total_posts': published_posts.count(),
        'active_authors': published_posts.values('author').distinct().count(),
        'category_count': Category.objects.count(),
        'founder': User.objects.order_by('date_joined').first(),
        'top_authors': top_authors,
    }
    return render(request, 'core/about.html', context)
# blog/views.py (or wherever your views are)

from django.db.models import Count, Q, Sum
from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta

from blog.models import Post, Category, Tag, Newsletter


def home(request):
    """
    Ultra-fast, fully compatible homepage view for the new
 magazine-style ModernBlog homepage.
    """
    
    # 1. Featured Posts – 1 hero + up to 4 side cards (max 5)
    featured_posts = (
        Post.objects.filter(status='published', is_featured=True)
        .select_related('author', 'category')
        .prefetch_related('tags')
        .order_by('-published_at')[:5]
    )

    # 2. Latest Posts – 8 for the "Latest Articles" grid
    latest_posts = (
        Post.objects.filter(status='published')
        .select_related('author', 'category')
        .prefetch_related('tags')
        .order_by('-published_at')[:8]
    )

    # 3. Categories – with post count (using your model's method via annotation)
    categories = (
        Category.objects.annotate(
            num_posts=Count(
                'posts',
                filter=Q(posts__status='published')
            )
        )
        .filter(num_posts__gt=0)
        .order_by('-num_posts', 'name')[:12]
    )

    # 4. Popular Tags – top 24 by usage
    popular_tags = (
        Tag.objects.annotate(
            post_count=Count(
                'posts',
                filter=Q(posts__status='published')
            )
        )
        .filter(post_count__gt=0)
        .order_by('-post_count', 'name')[:24]
    )

    # 5. Dynamic Statistics
    total_posts = Post.objects.filter(status='published').count()

    total_views = (
        Post.objects.filter(status='published')
        .aggregate(total=Sum('views'))['total'] or 0
    )

    newsletter_count = Newsletter.objects.filter(is_active=True).count()

    total_authors = (
        Post.objects.filter(status='published')
        .values('author').distinct()
        .count()
    )

    # Posts this month – for the live badge
    now = timezone.now()
    posts_this_month = Post.objects.filter(
        status='published',
        published_at__year=now.year,
        published_at__month=now.month,
    ).count()

    # 6. Trending Posts (last 30 days, high views) – for optional "Trending" badge
    thirty_days_ago = now - timedelta(days=30)
    trending_post_ids = list(
        Post.objects.filter(
            status='published',
            published_at__gte=thirty_days_ago
        )
        .order_by('-views')[:10]
        .values_list('id', flat=True)
    )

    context = {
        # Main sections
        'featured_posts': featured_posts,
        'posts': latest_posts,  # renamed for clarity
        'categories': categories,
        'popular_tags': popular_tags,

        # Stats (used in hero + newsletter)
        'total_posts': total_posts,
        'total_views': total_views,
        'newsletter_count': newsletter_count,
        'total_authors': total_authors,
        'posts_this_month': posts_this_month,

        # Optional: for "Trending" badge in template
        'trending_post_ids': trending_post_ids,

        # SEO
        'page_title': 'ModernBlog – Professional Insights & Articles',
        'page_description': 'Deep dives into software engineering, leadership, and innovation.',
    }

    return render(request, 'core/home.html', context)

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



# core/views.py
from django.views.generic import TemplateView
from django.urls import reverse_lazy


class CookiePolicyView(TemplateView):
    template_name = "core/cookie_policy.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "page_title": "Cookie Policy",
            "meta_description": "Learn how ModernBlog uses cookies and similar technologies to improve your experience, "
                              "provide essential functionality, and analyze site performance.",
            "current_year": 2025,
        })
        return context
    
    
    

class PrivacyPolicyView(TemplateView):
    template_name = "core/privacy_policy.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "page_title": "Privacy Policy - ModernBlog",
            "meta_description": "Read ModernBlog's Privacy Policy to understand how we collect, "
                              "use, and protect your personal information when you use our website.",
            "canonical_url": self.request.build_absolute_uri(
                reverse_lazy("core:privacy_policy")
            ),
        })
        return context
    
    
    
    

class TermsView(TemplateView):
    template_name = "core/terms.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["canonical_url"] = self.request.build_absolute_uri(
            reverse_lazy("core:terms")
        )
        return context


class FAQView(TemplateView):
    template_name = "core/faq.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["canonical_url"] = self.request.build_absolute_uri(
            reverse_lazy("core:faq")
        )
        return context