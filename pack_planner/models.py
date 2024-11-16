from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.core.validators import MinValueValidator

# Permission functions
def create_pack_upload_permission():
    """Create custom permission for pack data uploads"""
    content_type = ContentType.objects.get_for_model(Category)  # Using Category as the base model
    permission, created = Permission.objects.get_or_create(
        codename='pack_planner_data_upload_permission',
        name='Can upload pack planning data',
        content_type=content_type,
    )
    return permission

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    importance = models.CharField(
        max_length=20,
        choices=[
            ('critical', 'Critical - Required for survival'),
            ('recommended', 'Recommended - Significantly improves chances'),
            ('optional', 'Optional - Additional support')
        ]
    )
    order = models.IntegerField(default=0)
    
    class Meta:
        verbose_name_plural = "categories"
        ordering = ['order', 'name']
        permissions = [
            ("pack_planner_data_upload_permission", "Can upload pack planning data"),
        ]

class Item(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    uses = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    importance = models.CharField(
        max_length=20,
        choices=[
            ('critical', 'Critical'),
            ('recommended', 'Recommended'),
            ('optional', 'Optional')
        ]
    )
    weight_note = models.CharField(max_length=100, blank=True, help_text="e.g. 'Light', 'Heavy', 'One per person'")
    special_considerations = models.TextField(blank=True, help_text="Notes about children, elderly, pets, etc.")
    alternatives = models.ManyToManyField('self', blank=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['category', 'order', 'name']

class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='recommended_products')
    url = models.URLField(blank=True)
    notes = models.TextField(blank=True)
    is_available = models.BooleanField(default=True)
    last_verified = models.DateTimeField(auto_now=True)