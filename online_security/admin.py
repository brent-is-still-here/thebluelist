
from django.contrib import admin
from .models import SecurityCategory, SecurityItem, Recommendation
from .management.commands.populate_security_data import SecurityDataAdmin

@admin.register(SecurityCategory)
class SecurityCategoryAdmin(SecurityDataAdmin, admin.ModelAdmin):
    list_display = ('name', 'order')

@admin.register(SecurityItem)
class SecurityItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'difficulty', 'importance', 'order')
    list_filter = ('category', 'difficulty', 'importance')

@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ('title', 'security_item', 'order')
    list_filter = ('security_item',)