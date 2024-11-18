from django.contrib import admin, messages
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import path, reverse
from django.core.management import call_command
from .models import (
    ServiceCategory, ProductCategory, Location,
    Business, PoliticalData, EditRequest, DataSource
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

# Step 1: Add PoliticalDataInline for editing political data within a business
class PoliticalDataInline(admin.StackedInline):
    model = PoliticalData
    extra = 0
    can_delete = False
    readonly_fields = ('overall_conservative_percentage', 'overall_liberal_percentage')


# Step 2: Add EditRequestInline for identifying update requests within a business
class EditRequestInline(admin.TabularInline):
    model = EditRequest
    extra = 0
    fields = ('submitted_by', 'status', 'justification', 'created_at', 'reviewed_at')
    readonly_fields = ('created_at', 'reviewed_at')

@admin.register(ServiceCategory)
class ServiceCategoryAdmin(CategoryImportMixin, admin.ModelAdmin):
    list_display = ('name', 'parent', 'slug')
    search_fields = ('name',)
    list_filter = ('parent',)
    prepopulated_fields = {'slug': ('name',)}
    raw_id_fields = ('parent',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('parent')

@admin.register(ProductCategory)
class ProductCategoryAdmin(CategoryImportMixin, admin.ModelAdmin):
    list_display = ('name', 'parent', 'slug')
    search_fields = ('name',)
    list_filter = ('parent',)
    prepopulated_fields = {'slug': ('name',)}
    raw_id_fields = ('parent',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('parent')

# Step 3: Updated BusinessAdmin to include inlines
@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ('name', 'website', 'provides_services', 'provides_products', 'created_at', 'updated_at')
    search_fields = ('name', 'description', 'website')
    list_filter = ('provides_services', 'provides_products', 'locations')
    filter_horizontal = ('services', 'products', 'locations')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [PoliticalDataInline, EditRequestInline]  # Added inlines here


@admin.register(PoliticalData)
class PoliticalDataAdmin(admin.ModelAdmin):
    list_display = (
        'business', 
        'get_direct_conservative_pct', 
        'get_direct_liberal_pct',
        'get_pac_conservative_pct',
        'get_pac_liberal_pct',
        'direct_america_pac_donor',
        'direct_save_america_pac_donor',
        'senior_employee_trump_donor',
        'last_updated'
    )
    search_fields = ('business__name', 'data_source')
    list_filter = (
        'direct_america_pac_donor',
        'direct_save_america_pac_donor',
        'affiliated_pac_america_pac_donor',
        'affiliated_pac_save_america_pac_donor',
        'senior_employee_trump_donor',
        'senior_employee_america_pac_donor',
        'senior_employee_save_america_pac_donor'
    )

    def get_direct_conservative_pct(self, obj):
        return f"{obj.direct_conservative_percentage:.1f}%" if obj.direct_conservative_percentage else "N/A"
    get_direct_conservative_pct.short_description = "Direct Cons %"

    def get_direct_liberal_pct(self, obj):
        return f"{obj.direct_liberal_percentage:.1f}%" if obj.direct_liberal_percentage else "N/A"
    get_direct_liberal_pct.short_description = "Direct Lib %"

    def get_pac_conservative_pct(self, obj):
        return f"{obj.affiliated_pac_conservative_percentage:.1f}%" if obj.affiliated_pac_conservative_percentage else "N/A"
    get_pac_conservative_pct.short_description = "PAC Cons %"

    def get_pac_liberal_pct(self, obj):
        return f"{obj.affiliated_pac_liberal_percentage:.1f}%" if obj.affiliated_pac_liberal_percentage else "N/A"
    get_pac_liberal_pct.short_description = "PAC Lib %"


@admin.register(EditRequest)
class EditRequestAdmin(admin.ModelAdmin):
    list_display = ('business', 'submitted_by', 'status', 'justification', 'created_at', 'reviewed_at')
    search_fields = ('business__name', 'submitted_by__username', 'justification', 'review_notes')
    list_filter = ('status',)
    filter_horizontal = ('services_to_add', 'services_to_remove', 'products_to_add', 'products_to_remove')
    readonly_fields = ('created_at', 'reviewed_at')

    fieldsets = (
        ('Basic Information', {
            'fields': ('business', 'submitted_by', 'status', 'justification', 'supporting_links')
        }),
        ('Direct Donation Changes', {
            'fields': (
                'direct_conservative_total_donations',
                'direct_liberal_total_donations',
                'direct_total_donations',
                'direct_america_pac_donor',
                'direct_save_america_pac_donor',
            )
        }),
        ('PAC Donation Changes', {
            'fields': (
                'affiliated_pac_conservative_total_donations',
                'affiliated_pac_liberal_total_donations',
                'affiliated_pac_total_donations',
                'affiliated_pac_america_pac_donor',
                'affiliated_pac_save_america_pac_donor',
            )
        }),
        ('Senior Employee Activity Changes', {
            'fields': (
                'senior_employee_trump_donor',
                'senior_employee_america_pac_donor',
                'senior_employee_save_america_pac_donor',
            )
        }),
        ('Service Changes', {
            'fields': ('provides_services', 'services_to_add', 'services_to_remove')
        }),
        ('Product Changes', {
            'fields': ('provides_products', 'products_to_add', 'products_to_remove')
        }),
        ('Review Information', {
            'fields': ('reviewed_by', 'reviewed_at', 'review_notes')
        }),
    )


# Step 4: Register DataSource model
@admin.register(DataSource)
class DataSourceAdmin(admin.ModelAdmin):
    list_display = ('business', 'url', 'reason', 'is_approved', 'created_at')
    search_fields = ('business__name', 'url', 'reason')
    list_filter = ('is_approved', 'reason')
    ordering = ('-created_at',)
