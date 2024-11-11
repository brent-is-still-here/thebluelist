from django.contrib import admin

from .models import (
    ServiceCategory, ProductCategory, Location,
    Business, PoliticalData, EditRequest
)

# Register ServiceCategory
@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'slug')
    search_fields = ('name', 'parent')

# Register ProductCategory
@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'slug')
    search_fields = ('name', 'parent')

# Register Location
@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('city', 'state', 'zip_code', 'latitude', 'longitude')
    search_fields = ('city', 'state', 'zip_code')
    list_filter = ('state',)

# Register Business
@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ('name', 'website', 'provides_services', 'provides_products', 'created_at', 'updated_at')
    search_fields = ('name', 'description', 'website')
    list_filter = ('provides_services', 'provides_products', 'locations')
    filter_horizontal = ('services', 'products', 'locations')
    prepopulated_fields = {'slug': ('name',)}

# Register PoliticalData
@admin.register(PoliticalData)
class PoliticalDataAdmin(admin.ModelAdmin):
    list_display = ('business', 'conservative_percentage', 'liberal_percentage', 'trump_donor', 'america_pac_donor', 'save_america_pac_donor', 'last_updated')
    search_fields = ('business__name', 'data_source')
    list_filter = ('trump_donor', 'america_pac_donor', 'save_america_pac_donor')

# Register EditRequest
@admin.register(EditRequest)
class EditRequestAdmin(admin.ModelAdmin):
    list_display = ('business', 'submitted_by', 'status', 'justification', 'created_at', 'reviewed_at')
    search_fields = ('business__name', 'submitted_by__username', 'justification', 'review_notes')
    list_filter = ('status',)
    filter_horizontal = ('services_to_add', 'services_to_remove', 'products_to_add', 'products_to_remove')
    readonly_fields = ('created_at', 'reviewed_at')

