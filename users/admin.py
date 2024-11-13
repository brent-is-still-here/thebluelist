from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, HashedEmail

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

@admin.register(HashedEmail)
class HashedEmailAdmin(admin.ModelAdmin):
    list_display = ('email_hash', 'first_used', 'last_used', 'total_users',
                   'active_users', 'is_blocked')
    list_filter = ('is_blocked', 'first_used', 'last_used')
    search_fields = ('email_hash',)
    actions = ['block_selected_hashes', 'unblock_selected_hashes']

    def total_users(self, obj):
        return obj.get_total_users_count()
    total_users.short_description = 'Total Users'

    def active_users(self, obj):
        return obj.get_active_users_count()
    active_users.short_description = 'Active Users (30d)'

    def block_selected_hashes(self, request, queryset):
        queryset.update(is_blocked=True)
    block_selected_hashes.short_description = "Block selected email hashes"

    def unblock_selected_hashes(self, request, queryset):
        queryset.update(is_blocked=False)
    unblock_selected_hashes.short_description = "Unblock selected email hashes"