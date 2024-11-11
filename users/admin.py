from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # Fields to display in the admin list view
    list_display = ('username', 'email', 'first_name', 'last_name', 'email_verified', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'email_verified')
    
    # Fields to include in the user detail view
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('email_verified', 'verification_token')
        }),
    )
    
    # Fields to include when creating a new user
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('email_verified', 'verification_token')
        }),
    )

    # Fields that are read-only
    readonly_fields = ('last_login', 'date_joined')

