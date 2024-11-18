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
        max_length=15,
        choices=[
            ('critical', 'Critical'),
            ('recommended', 'Recommended'),
            ('optional', 'Optional')
        ]
    )
    go_bag = models.BooleanField(default=True)
    seventy_two_hr_bag = models.BooleanField(default=True)
    order = models.IntegerField(default=0)

    def __str__(self):
        return self.name
    
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
    category = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE, 
        related_name='items')
    importance = models.CharField(
        max_length=20,
        choices=[
            ('critical', 'Critical'),
            ('recommended', 'Recommended'),
            ('optional', 'Optional')
        ]
    )
    weight_note = models.CharField(max_length=100, blank=True, help_text="e.g. 'Light', 'Heavy', 'One per person'")
    special_considerations = models.TextField(blank=True, help_text="Special concerns, regulations, etc.")
    alternatives = models.ManyToManyField('self', blank=True)
    order = models.IntegerField(default=0)

    conditional_applicability = models.BooleanField(default=False)
    for_adults = models.BooleanField(default=True)
    for_children = models.BooleanField(default=False)
    for_pets = models.BooleanField(default=False)
    for_cats = models.BooleanField(default=False)
    for_dogs = models.BooleanField(default=False)
    for_small_animals = models.BooleanField(default=False)
    for_disabled = models.BooleanField(default=False)
    for_elderly = models.BooleanField(default=False)
    for_on_foot = models.BooleanField(default=True)
    for_bicycle = models.BooleanField(default=True)
    for_vehicle = models.BooleanField(default=True)
    for_public_transit = models.BooleanField(default=True)
    go_bag = models.BooleanField(default=True)
    seventy_two_hr_bag = models.BooleanField(default=True)

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
    
    go_bag = models.BooleanField(default=True)
    seventy_two_hr_bag = models.BooleanField(default=True)