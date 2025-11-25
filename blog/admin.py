# blog/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Tag, Post, Comment, Newsletter


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'post_count', 'icon', 'color', 'created_at']
    list_editable = ['icon', 'color']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'description']
    list_per_page = 20

    def post_count(self, obj):
        return obj.post_count()  # Uses your model's method
    post_count.short_description = 'Posts'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'post_count']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']
    list_per_page = 30

    def post_count(self, obj):
        return obj.posts.filter(status='published').count()
    post_count.short_description = 'Posts'


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'author', 'category', 'status', 'is_featured',
        'views', 'like_count', 'reading_time', 'published_at', 'created_at'
    ]
    list_filter = [
        'status', 'is_featured', 'category', 'tags', 'created_at', 'published_at'
    ]
    search_fields = [
        'title', 'excerpt', 'content_html', 'content_markdown',
        'author__username', 'author__first_name', 'author__last_name'
    ]
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ['tags', 'likes']
    readonly_fields = ['views', 'created_at', 'updated_at', 'published_at_preview']
    date_hierarchy = 'published_at'
    list_editable = ['is_featured', 'status']
    list_per_page = 20
    actions = ['make_published', 'make_draft', 'mark_as_featured']

    fieldsets = (
        ('Basic Info', {
            'fields': ('title', 'slug', 'author', 'category', 'tags', 'featured_image')
        }),
        ('Content', {
            'fields': ('excerpt', 'content_type', ('content_html', 'content_markdown'))
        }),
        ('Publication', {
            'fields': ('status', 'is_featured', 'published_at'),
            'description': 'Set published_at automatically when status → Published'
        }),
        ('Stats (Read-only)', {
            'fields': ('views', 'likes', 'created_at', 'updated_at', 'published_at_preview'),
            'classes': ('collapse',)
        }),
    )

    def published_at_preview(self, obj):
        if obj.published_at:
            return obj.published_at.strftime('%b %d, %Y at %I:%M %p')
        return "Not published yet"
    published_at_preview.short_description = 'Published On'

    def save_model(self, request, obj, form, change):
        # Auto-set published_at when status changes to 'published'
        if obj.status == 'published' and not obj.published_at:
            obj.published_at = timezone.now()
        super().save_model(request, obj, form, change)

    # Custom actions
    def make_published(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(status='published')
        for post in queryset:
            if not post.published_at:
                post.published_at = timezone.now()
                post.save()
        self.message_user(request, f'{updated} post(s) published.')
    make_published.short_description = "Publish selected posts"

    def make_draft(self, request, queryset):
        updated = queryset.update(status='draft', published_at=None)
        self.message_user(request, f'{updated} post(s) set to draft.')
    make_draft.short_description = "Set selected posts to draft"

    def mark_as_featured(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} post(s) marked as featured.')
    mark_as_featured.short_description = "Mark as featured"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['post', 'author', 'short_content', 'created_at', 'is_approved']
    list_filter = ['is_approved', 'created_at', 'post__category']
    search_fields = ['content', 'author__username', 'author__email', 'post__title']
    readonly_fields = ['created_at', 'updated_at']
    actions = ['approve_comments', 'unapprove_comments']

    def short_content(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    short_content.short_description = 'Comment'

    def approve_comments(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'{updated} comment(s) approved.')
    approve_comments.short_description = "Approve selected comments"

    def unapprove_comments(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'{updated} comment(s) unapproved.')
    unapprove_comments.short_description = "Unapprove selected comments"


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ['email', 'subscribed_at', 'is_active']
    list_filter = ['is_active', 'subscribed_at']
    search_fields = ['email']
    readonly_fields = ['subscribed_at']
    actions = ['mark_active', 'mark_inactive']

    def mark_active(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} subscriber(s) activated.')
    mark_active.short_description = "Mark as active"

    def mark_inactive(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} subscriber(s) deactivated.')
    mark_inactive.short_description = "Mark as inactive"