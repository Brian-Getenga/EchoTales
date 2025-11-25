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