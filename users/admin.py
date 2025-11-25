from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('bio', 'avatar', 'website', 'twitter', 'github', 'linkedin', 'location')
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('bio', 'avatar', 'website', 'twitter', 'github', 'linkedin', 'location')
        }),
    )