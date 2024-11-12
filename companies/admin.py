from django.contrib import admin, messages
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import path, reverse
from django.core.management import call_command
from .models import (
    ServiceCategory, ProductCategory, Location,
    Business, PoliticalData, EditRequest
)

class CategoryImportMixin:
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'import-categories/',
                self.admin_site.admin_view(self.import_categories_view),
                name='import_categories',
            ),
        ]
        return custom_urls + urls

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_import_button'] = True
        return super().changelist_view(request, extra_context)

    def import_categories_view(self, request):
        try:
            call_command('import_categories')
            self.message_user(request, 'Categories imported successfully!', messages.SUCCESS)
        except Exception as e:
            self.message_user(request, f'Error importing categories: {str(e)}', level=messages.ERROR)
        
        return HttpResponseRedirect(reverse('admin:companies_productcategory_changelist'))

@admin.register(ProductCategory)
class ProductCategoryAdmin(CategoryImportMixin, admin.ModelAdmin):
    list_display = ('name', 'parent', 'slug')
    search_fields = ('name', 'parent__name')
    list_filter = ('parent',)

@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'slug')
    search_fields = ('name', 'parent__name')
    list_filter = ('parent',)

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('city', 'state', 'zip_code', 'latitude', 'longitude')
    search_fields = ('city', 'state', 'zip_code')
    list_filter = ('state',)

@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ('name', 'website', 'provides_services', 'provides_products', 'created_at', 'updated_at')
    search_fields = ('name', 'description', 'website')
    list_filter = ('provides_services', 'provides_products', 'locations')
    filter_horizontal = ('services', 'products', 'locations')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(PoliticalData)
class PoliticalDataAdmin(admin.ModelAdmin):
    list_display = ('business', 'conservative_percentage', 'liberal_percentage', 
                   'trump_donor', 'america_pac_donor', 'save_america_pac_donor', 'last_updated')
    search_fields = ('business__name', 'data_source')
    list_filter = ('trump_donor', 'america_pac_donor', 'save_america_pac_donor')

@admin.register(EditRequest)
class EditRequestAdmin(admin.ModelAdmin):
    list_display = ('business', 'submitted_by', 'status', 'justification', 'created_at', 'reviewed_at')
    search_fields = ('business__name', 'submitted_by__username', 'justification', 'review_notes')
    list_filter = ('status',)
    filter_horizontal = ('services_to_add', 'services_to_remove', 'products_to_add', 'products_to_remove')
    readonly_fields = ('created_at', 'reviewed_at')