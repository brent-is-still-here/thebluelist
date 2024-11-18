from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from .models import Category, Item, Product

class ProductInline(admin.TabularInline):
    model = Product
    extra = 1
    fields = ('name', 'description', 'url', 'is_available', 'last_verified')
    readonly_fields = ('last_verified',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'importance', 'order', 'item_count')
    list_filter = ('importance',)
    search_fields = ('name', 'description')
    ordering = ('order', 'name')
    
    def item_count(self, obj):
        count = obj.items.count()
        return format_html(
            '<a href="{}?category={}">{} items</a>',
            reverse('admin:pack_planner_item_changelist'),
            obj.id,
            count
        )
    item_count.short_description = 'Items'

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = (
        'name', 
        'category', 
        'importance', 
        'weight_note',
        'product_count',
        'has_special_considerations',
        'for_adults',
        'for_children',
        'for_pets',
    )
    list_filter = ('importance', 'category', 'for_adults', 'for_children', 'for_pets', 'for_disabled', 'for_elderly')
    search_fields = ('name', 'description', 'uses', 'special_considerations')
    ordering = ('category', 'order', 'name')
    inlines = [ProductInline]
    filter_horizontal = ('alternatives',)
    
    fieldsets = (
        (None, {
            'fields': (
                'name', 
                'description', 
                'uses', 
                'category', 
                'importance', 
                'order'
            )
        }),
        ('Details', {
            'fields': (
                'weight_note', 
                'special_considerations', 
                'alternatives',
                'conditional_applicability',
                'for_adults', 
                'for_children', 
                'for_pets', 
                'for_disabled', 
                'for_elderly',
                'for_on_foot', 
                'for_bicycle', 
                'for_vehicle', 
                'for_public_transit'
            ),
            'classes': ('collapse',)
        })
    )

    def product_count(self, obj):
        count = obj.recommended_products.count()
        if count:
            return format_html(
                '<a href="{}?item={}">{} products</a>',
                reverse('admin:pack_planner_product_changelist'),
                obj.id,
                count
            )
        return '0 products'
    product_count.short_description = 'Products'

    def has_special_considerations(self, obj):
        return bool(obj.special_considerations)
    has_special_considerations.boolean = True
    has_special_considerations.short_description = 'Special Needs'

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'item',
        'category_name',
        'is_available',
        'last_verified',
        'url_link'
    )
    list_filter = (
        'is_available', 
        'item__category',
        'last_verified'
    )
    search_fields = (
        'name',
        'description',
        'notes',
        'item__name'
    )
    readonly_fields = ('last_verified',)
    
    def category_name(self, obj):
        return obj.item.category.name
    category_name.short_description = 'Category'
    
    def url_link(self, obj):
        if obj.url:
            return format_html(
                '<a href="{}" target="_blank" rel="noopener noreferrer">View →</a>',
                obj.url
            )
        return '-'
    url_link.short_description = 'Link'

# Make the data upload permission visible in admin
class DataUploadPermissionAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        return super().get_queryset(request).filter(
            codename='pack_planner_data_upload_permission'
        )
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False

# Register the permission
try:
    admin.site.register(
        Permission, 
        DataUploadPermissionAdmin, 
        verbose_name_plural='Pack Planner Permissions'
    )
except admin.sites.AlreadyRegistered:
    pass

# Admin actions for products
@admin.action(description='Mark selected products as available')
def make_available(modeladmin, request, queryset):
    queryset.update(is_available=True)

@admin.action(description='Mark selected products as unavailable')
def make_unavailable(modeladmin, request, queryset):
    queryset.update(is_available=False)

# Add actions to ProductAdmin
ProductAdmin.actions = [make_available, make_unavailable]

# Customize admin site headers
admin.site.site_header = 'Pack Planner Administration'
admin.site.site_title = 'Pack Planner Admin'
admin.site.index_title = 'Pack Planning Management'