from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.conf import settings

class BaseModel(models.Model):
    """Abstract base model with common fields"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="%(class)s_created"
    )
    last_modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="%(class)s_modified"
    )

    class Meta:
        abstract = True

class Country(BaseModel):
    """Core country information"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    official_languages = models.ManyToManyField('Language', related_name='countries')
    business_language = models.ForeignKey(
        'Language',
        on_delete=models.SET_NULL,
        null=True,
        related_name='business_countries'
    )
    currency = models.CharField(max_length=50)
    capital_city = models.CharField(max_length=100)
    population = models.PositiveIntegerField()
    timezone = models.CharField(max_length=50)
    
    # Automatically updated statistics
    avg_cost_of_living = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    avg_house_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )
    avg_rent_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "countries"

class Language(BaseModel):
    """Language information"""
    name = models.CharField(max_length=50, unique=True)
    code = models.CharField(max_length=10, unique=True)  # ISO code

class Rating(BaseModel):
    """User ratings for various country aspects"""
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    category = models.CharField(max_length=50, choices=[
        ('SAFETY', 'Safety'),
        ('HEALTHCARE', 'Healthcare Quality'),
        ('EDUCATION', 'Education Quality'),
        ('HAPPINESS', 'Overall Happiness'),
        ('INFRASTRUCTURE', 'Infrastructure'),
        ('FOREIGNER_FRIENDLY', 'Foreigner Friendliness'),
        ('WORK_LIFE', 'Work-Life Balance'),
        ('ENVIRONMENT', 'Environmental Quality')
    ])
    score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True)

    class Meta:
        unique_together = ['country', 'user', 'category']

class VisaType(BaseModel):
    """Different types of visas available"""
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()
    duration = models.CharField(max_length=50)
    processing_time = models.CharField(max_length=50)
    allows_family = models.BooleanField()
    family_notes = models.TextField(blank=True)
    can_work = models.BooleanField()
    path_to_citizenship = models.BooleanField()
    
    class Meta:
        unique_together = ['country', 'name']

class VisaRequirement(BaseModel):
    """Requirements for specific visa types"""
    visa_type = models.ForeignKey(VisaType, on_delete=models.CASCADE)
    requirement = models.CharField(max_length=255)
    details = models.TextField()
    is_mandatory = models.BooleanField(default=True)

class CostOfLiving(BaseModel):
    """User-submitted cost of living data"""
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    city = models.CharField(max_length=100)
    date_recorded = models.DateField()
    
    # Monthly costs
    rent_1bed_city = models.DecimalField(max_digits=10, decimal_places=2)
    rent_3bed_city = models.DecimalField(max_digits=10, decimal_places=2)
    rent_1bed_suburban = models.DecimalField(max_digits=10, decimal_places=2)
    rent_3bed_suburban = models.DecimalField(max_digits=10, decimal_places=2)
    utilities = models.DecimalField(max_digits=8, decimal_places=2)
    internet = models.DecimalField(max_digits=8, decimal_places=2)
    groceries = models.DecimalField(max_digits=8, decimal_places=2)
    transportation = models.DecimalField(max_digits=8, decimal_places=2)
    
    class Meta:
        verbose_name_plural = "costs of living"

class PropertyCost(BaseModel):
    """User-submitted property cost data"""
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    city = models.CharField(max_length=100)
    date_recorded = models.DateField()
    property_type = models.CharField(max_length=50, choices=[
        ('APARTMENT', 'Apartment'),
        ('HOUSE', 'House'),
        ('LAND', 'Land')
    ])
    size_sqm = models.DecimalField(max_digits=8, decimal_places=2)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    location_type = models.CharField(max_length=20, choices=[
        ('CITY_CENTER', 'City Center'),
        ('SUBURBAN', 'Suburban'),
        ('RURAL', 'Rural')
    ])

class RelocationProcess(BaseModel):
    """Documentation of relocation processes"""
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    step_number = models.PositiveIntegerField()
    title = models.CharField(max_length=200)
    description = models.TextField()
    estimated_time = models.CharField(max_length=50)
    estimated_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    required_documents = models.TextField()
    
    class Meta:
        unique_together = ['country', 'step_number']
        ordering = ['step_number']

class PetRelocationRequirement(BaseModel):
    """Requirements for relocating with pets"""
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    pet_type = models.CharField(max_length=50)  # dog, cat, bird, etc.
    quarantine_required = models.BooleanField()
    quarantine_duration = models.CharField(max_length=50, blank=True)
    vaccination_requirements = models.TextField()
    documentation_required = models.TextField()
    restrictions = models.TextField(blank=True)
    estimated_cost = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True
    )

class CitizenshipProcess(BaseModel):
    """Documentation of naturalization processes"""
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    residence_requirement_years = models.PositiveIntegerField()
    language_requirement = models.TextField()
    dual_citizenship_allowed = models.BooleanField()
    test_required = models.BooleanField()
    test_details = models.TextField(blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    process_details = models.TextField()
    
class HealthcareInfo(BaseModel):
    """Healthcare system information"""
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    has_universal_healthcare = models.BooleanField()
    immigrant_coverage_waiting_period = models.CharField(max_length=100)
    private_insurance_requirement = models.TextField()
    avg_cost_private_insurance = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True
    )
    healthcare_system_details = models.TextField()

class ResourceLink(BaseModel):
    """External resources and references"""
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    url = models.URLField()
    category = models.CharField(max_length=50, choices=[
        ('OFFICIAL', 'Official Government Resource'),
        ('HEALTHCARE', 'Healthcare Information'),
        ('HOUSING', 'Housing Information'),
        ('EDUCATION', 'Education Information'),
        ('VISA', 'Visa Information'),
        ('EMPLOYMENT', 'Employment Information'),
        ('COMMUNITY', 'Community Resource')
    ])
    description = models.TextField()
    is_verified = models.BooleanField(default=False)

class UserExperience(BaseModel):
    """User experiences and stories"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    moved_from = models.CharField(max_length=100)
    year_moved = models.PositiveIntegerField()
    current_status = models.CharField(max_length=50, choices=[
        ('PLANNING', 'Planning Stage'),
        ('IN_PROGRESS', 'Currently Relocating'),
        ('RELOCATED', 'Successfully Relocated'),
        ('RETURNED', 'Returned to Origin')
    ])
    would_recommend = models.BooleanField()
    challenges_faced = models.TextField()
    tips = models.TextField()

class EditHistory(BaseModel):
    """Track changes to content"""
    content_type = models.ForeignKey('contenttypes.ContentType', on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    field_name = models.CharField(max_length=100)
    old_value = models.TextField(blank=True)
    new_value = models.TextField(blank=True)
    change_reason = models.TextField()
    