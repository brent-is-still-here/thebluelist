from django.db import models
from django.contrib.auth.models import User

class BusinessCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    slug = models.SlugField(unique=True)

class Location(models.Model):
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=2)
    zip_code = models.CharField(max_length=10)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)

class Business(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    website = models.URLField(blank=True)
    description = models.TextField()
    categories = models.ManyToManyField(BusinessCategory)
    locations = models.ManyToManyField(Location)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class PoliticalData(models.Model):
    business = models.OneToOneField(Business, on_delete=models.CASCADE)
    republican_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    democrat_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    trump_donor = models.BooleanField(default=False)
    america_pac_donor = models.BooleanField(default=False)
    total_donations = models.DecimalField(max_digits=12, decimal_places=2)
    data_source = models.TextField()
    last_updated = models.DateTimeField(auto_now=True)

class EditRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ]
    
    business = models.ForeignKey(Business, on_delete=models.CASCADE)
    submitted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
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
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='reviewed_edits'
    )
    review_notes = models.TextField(blank=True)