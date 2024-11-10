from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.text import slugify

class BusinessCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    slug = models.SlugField(unique=True)

class ServiceCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    slug = models.SlugField(unique=True)
    
    class Meta:
        verbose_name_plural = "Service Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class ProductCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    slug = models.SlugField(unique=True)
    
    class Meta:
        verbose_name_plural = "Product Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Location(models.Model):
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=2)
    zip_code = models.CharField(max_length=10)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)

class Business(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    website = models.URLField(null=True, blank=True)
    description = models.TextField()
    
    # Company relationships
    parent_company = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='subsidiaries'
    )
    
    # Categories and Locations
    categories = models.ManyToManyField(BusinessCategory)
    locations = models.ManyToManyField(Location)
    
    # Services
    provides_services = models.BooleanField(default=False)
    services = models.ManyToManyField(
        ServiceCategory,
        blank=True,
        related_name='service_providers'
    )
    
    # Products
    provides_products = models.BooleanField(default=False)
    products = models.ManyToManyField(
        ProductCategory,
        blank=True,
        related_name='product_providers'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Businesses"
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    @property
    def all_subsidiaries(self):
        """Returns all subsidiaries (recursive)"""
        subs = list(self.subsidiaries.all())
        for sub in self.subsidiaries.all():
            subs.extend(sub.all_subsidiaries)
        return subs
    
    @property
    def ultimate_parent(self):
        """Returns the topmost parent company"""
        if not self.parent_company:
            return self
        return self.parent_company.ultimate_parent

class PoliticalData(models.Model):
    business = models.OneToOneField(Business, on_delete=models.CASCADE)
    conservative_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    conservative_total_donations = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    liberal_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    liberal_total_donations = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    trump_donor = models.BooleanField(default=False)
    america_pac_donor = models.BooleanField(default=False)
    save_america_pac_donor = models.BooleanField(default=False)
    data_source = models.TextField()
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Political Data"

    def __str__(self):
        return f"Political data for {self.business.name}"

    @property
    def total_donations(self):
        return self.conservative_total_donations + self.liberal_total_donations

class EditRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ]
    
    business = models.ForeignKey(Business, on_delete=models.CASCADE)
    submitted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Changed data
    name = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    republican_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    democrat_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    trump_donor = models.BooleanField(null=True)
    america_pac_donor = models.BooleanField(null=True)
    total_donations = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    data_source = models.TextField(blank=True)
    
    justification = models.TextField()
    supporting_links = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='reviewed_edits'
    )
    review_notes = models.TextField(blank=True)