from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.text import slugify
from tinymce.models import HTMLField
from markdownx.models import MarkdownxField

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Emoji or icon class")
    color = models.CharField(max_length=20, default='blue', help_text="Tailwind color name")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('blog:category_posts', kwargs={'slug': self.slug})
    
    def post_count(self):
        return self.posts.filter(status='published').count()

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True, blank=True)
    
    class Meta:
        ordering = ['name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('blog:tag_posts', kwargs={'slug': self.slug})

class Post(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]
    
    CONTENT_TYPE_CHOICES = [
        ('html', 'HTML (TinyMCE)'),
        ('markdown', 'Markdown'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='posts')
    tags = models.ManyToManyField(Tag, blank=True, related_name='posts')
    
    excerpt = models.TextField(max_length=300, blank=True)
    featured_image = models.ImageField(upload_to='posts/', blank=True, null=True)
    
    content_type = models.CharField(max_length=10, choices=CONTENT_TYPE_CHOICES, default='html')
    content_html = HTMLField(blank=True)
    content_markdown = MarkdownxField(blank=True)
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    is_featured = models.BooleanField(default=False)
    
    views = models.PositiveIntegerField(default=0)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='liked_posts')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-published_at', '-created_at']
        indexes = [
            models.Index(fields=['-published_at']),
            models.Index(fields=['status']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'slug': self.slug})
    
    def get_content(self):
        if self.content_type == 'markdown':
            return self.content_markdown
        return self.content_html
    
    def reading_time(self):
        content = self.get_content()
        words = len(content.split())
        return max(1, words // 200)
    
    def like_count(self):
        return self.likes.count()

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_approved = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f'Comment by {self.author.username} on {self.post.title}'
    
    def children(self):
        return Comment.objects.filter(parent=self)

class Newsletter(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.email