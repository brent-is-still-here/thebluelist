from django.db import models
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

class Language(BaseModel):
    """Language information"""
    name = models.CharField(max_length=50, unique=True)
    code = models.CharField(max_length=10, unique=True)  # ISO code

    def __str__(self):
        return f"{self.name} ({self.code})"

class AnimalSpecies(BaseModel):
    """Animal species that can be relocated"""
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "animal species"

class VisaRequirement(BaseModel):
    visa = models.ForeignKey(
        'Visa',
        on_delete=models.CASCADE,
        related_name='requirement_list'
    )
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name

class Visa(BaseModel):
    country = models.ForeignKey(
        'Country',
        on_delete=models.CASCADE,
        related_name='visa_list'
    )
    name = models.CharField(max_length=100)
    description = models.TextField()
    duration = models.CharField(max_length=50)
    information_link = models.URLField()

    def __str__(self):
        return self.name

class PetRelocationRequirement(BaseModel):
    """Requirements for relocating with pets"""
    animal = models.ForeignKey(AnimalSpecies, on_delete=models.CASCADE)
    TYPE_CHOICES = [
        ('VACCINATION', 'Vaccination'),
        ('QUARANTINE', 'Quarantine'),
        ('DOCUMENTATION', 'Documentation'),
        ('FEE', 'Fee'),
    ]
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    duration = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.animal.name} - {self.get_type_display()} - {self.name}"

class Country(BaseModel):
    """Core country information"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    common_languages = models.ManyToManyField(Language, related_name='countries')
    business_language = models.ForeignKey(
        Language,
        on_delete=models.SET_NULL,
        null=True,
        related_name='business_countries'
    )
    cost_of_living_index = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )
    quality_of_life_index = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )
    has_universal_healthcare = models.BooleanField(default=False)
    pet_relocation_requirements = models.ManyToManyField(
        PetRelocationRequirement,
        related_name='countries'
    )
    pet_relocation_info_link = models.URLField(blank=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "countries"