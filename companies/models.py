from datetime import timezone
from django.db import models
from django.conf import settings
from django.contrib.auth.models import Permission, User
from django.contrib.contenttypes.models import ContentType
from django.utils.text import slugify

# Permission functions
def create_csv_import_permission():
    """Create custom permission for CSV imports"""
    content_type = ContentType.objects.get_for_model(Business)
    permission, created = Permission.objects.get_or_create(
        codename='can_import_business_csv',
        name='Can import business data via CSV',
        content_type=content_type,
    )
    return permission

# Models
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
    locations = models.ManyToManyField('Location', blank=True)
    
    # Services
    provides_services = models.BooleanField(default=False)
    services = models.ManyToManyField(
        'ServiceCategory',
        blank=True,
        related_name='service_providers'
    )
    
    # Products
    provides_products = models.BooleanField(default=False)
    products = models.ManyToManyField(
        'ProductCategory',
        blank=True,
        related_name='product_providers'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Businesses"
        ordering = ['name']
        permissions = [
            ("can_import_business_csv", "Can import business data via CSV"),
        ]

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
    
    def get_alternative_businesses(self, limit=10):
        """
        Find alternative businesses based on product/service similarity and political leanings.
        Returns businesses ordered by a weighted score.
        """
        # Get all products and services of this business
        my_products = set(self.products.values_list('id', flat=True))
        my_services = set(self.services.values_list('id', flat=True))
        total_offerings = len(my_products) + len(my_services)

        if total_offerings == 0:
            return Business.objects.none()

        # Get other businesses that share at least one product or service
        alternatives = Business.objects.exclude(id=self.id).filter(
            models.Q(products__in=my_products) | 
            models.Q(services__in=my_services)
        ).distinct()

        # Calculate similarity scores
        similarity_scores = []
        my_political_data = self.politicaldata

        for business in alternatives:
            # Calculate offering overlap
            their_products = set(business.products.values_list('id', flat=True))
            their_services = set(business.services.values_list('id', flat=True))
            
            product_overlap = len(my_products & their_products)
            service_overlap = len(my_services & their_services)
            total_overlap = product_overlap + service_overlap

            # Calculate offering similarity score (0 to 1)
            offering_score = total_overlap / total_offerings

            # Calculate political score (0 to 1, higher for more liberal businesses)
            try:
                # Convert Decimal to float before calculation
                conservative_pct = float(business.politicaldata.conservative_percentage)
                political_score = (100 - conservative_pct) / 100
            except (AttributeError, ZeroDivisionError):
                political_score = 0.5  # Default if no political data

            # Calculate weighted score
            # Weight offering similarity and political score equally
            weighted_score = (offering_score * 0.5) + (political_score * 0.5)

            similarity_scores.append({
                'business': business,
                'score': weighted_score,
                'overlap_count': total_overlap,
                'conservative_percentage': business.politicaldata.conservative_percentage if hasattr(business, 'politicaldata') else None
            })

        # Sort by weighted score
        similarity_scores.sort(key=lambda x: x['score'], reverse=True)
        
        return similarity_scores[:limit]

class CSVImportRateLimit(models.Model):
    """Track CSV import attempts for rate limiting"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    last_import_attempt = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'last_import_attempt'])
        ]

    @classmethod
    def can_import(cls, user):
        """Check if user can import based on rate limit"""
        last_import = cls.objects.filter(user=user).first()
        if not last_import:
            return True
            
        time_since_last = timezone.now() - last_import.last_import_attempt
        return time_since_last.total_seconds() > 30

class DataSource(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='data_sources')
    url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Data source for {self.business.name}"

class EditRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ]
    
    business = models.ForeignKey(Business, on_delete=models.CASCADE)
    submitted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Basic data changes
    name = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    
    # Direct donation changes
    direct_conservative_total_donations = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    direct_liberal_total_donations = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    direct_total_donations = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    direct_america_pac_donor = models.BooleanField(null=True)
    direct_save_america_pac_donor = models.BooleanField(null=True)
    
    # Affiliated PAC donation changes
    affiliated_pac_conservative_total_donations = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    affiliated_pac_liberal_total_donations = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    affiliated_pac_total_donations = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    affiliated_pac_america_pac_donor = models.BooleanField(null=True)
    affiliated_pac_save_america_pac_donor = models.BooleanField(null=True)
    
    # CEO donation changes
    ceo_trump_donor = models.BooleanField(null=True)
    ceo_america_pac_donor = models.BooleanField(null=True)
    ceo_save_america_pac_donor = models.BooleanField(null=True)
    
    # Data source
    data_source = models.TextField(blank=True)

    # Service changes
    provides_services = models.BooleanField(null=True)
    services_to_add = models.ManyToManyField(
        'ServiceCategory',
        related_name='edit_requests_adding',
        blank=True
    )
    services_to_remove = models.ManyToManyField(
        'ServiceCategory',
        related_name='edit_requests_removing',
        blank=True
    )
    
    # Product changes
    provides_products = models.BooleanField(null=True)
    products_to_add = models.ManyToManyField(
        'ProductCategory',
        related_name='edit_requests_adding',
        blank=True
    )
    products_to_remove = models.ManyToManyField(
        'ProductCategory',
        related_name='edit_requests_removing',
        blank=True
    )
    
    # Metadata
    justification = models.TextField()
    supporting_links = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='reviewed_edits'
    )
    review_notes = models.TextField(blank=True)

    class Meta:
        permissions = [
            ("can_review_edits", "Can review edit requests"),
        ]

    @property
    def direct_conservative_percentage(self):
        """Calculate percentage of direct conservative donations"""
        if not self.direct_total_donations:
            return None
        return (self.direct_conservative_total_donations or 0) / self.direct_total_donations * 100

    @property
    def direct_liberal_percentage(self):
        """Calculate percentage of direct liberal donations"""
        if not self.direct_total_donations:
            return None
        return (self.direct_liberal_total_donations or 0) / self.direct_total_donations * 100

    @property
    def affiliated_pac_conservative_percentage(self):
        """Calculate percentage of PAC conservative donations"""
        if not self.affiliated_pac_total_donations:
            return None
        return (self.affiliated_pac_conservative_total_donations or 0) / self.affiliated_pac_total_donations * 100

    @property
    def affiliated_pac_liberal_percentage(self):
        """Calculate percentage of PAC liberal donations"""
        if not self.affiliated_pac_total_donations:
            return None
        return (self.affiliated_pac_liberal_total_donations or 0) / self.affiliated_pac_total_donations * 100

class Location(models.Model):
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=2)
    zip_code = models.CharField(max_length=10)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)

class ServiceCategory(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='children'
    )
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

class PoliticalData(models.Model):
    business = models.OneToOneField(Business, on_delete=models.CASCADE)
    
    # Direct donation data
    direct_conservative_total_donations = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    direct_liberal_total_donations = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    direct_total_donations = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    direct_america_pac_donor = models.BooleanField(default=False)
    direct_save_america_pac_donor = models.BooleanField(default=False)
    
    # Affiliated PAC donation data
    affiliated_pac_conservative_total_donations = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    affiliated_pac_liberal_total_donations = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    affiliated_pac_total_donations = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    affiliated_pac_america_pac_donor = models.BooleanField(default=False)
    affiliated_pac_save_america_pac_donor = models.BooleanField(default=False)
    
    # CEO donation data
    ceo_trump_donor = models.BooleanField(default=False)
    ceo_america_pac_donor = models.BooleanField(default=False)
    ceo_save_america_pac_donor = models.BooleanField(default=False)
    
    # Metadata
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Political Data"

    def __str__(self):
        return f"Political data for {self.business.name}"

    @property
    def direct_conservative_percentage(self):
        """Calculate percentage of direct conservative donations"""
        if not self.direct_total_donations:
            return None
        return (self.direct_conservative_total_donations or 0) / self.direct_total_donations * 100

    @property
    def direct_liberal_percentage(self):
        """Calculate percentage of direct liberal donations"""
        if not self.direct_total_donations:
            return None
        return (self.direct_liberal_total_donations or 0) / self.direct_total_donations * 100

    @property
    def affiliated_pac_conservative_percentage(self):
        """Calculate percentage of PAC conservative donations"""
        if not self.affiliated_pac_total_donations:
            return None
        return (self.affiliated_pac_conservative_total_donations or 0) / self.affiliated_pac_total_donations * 100

    @property
    def affiliated_pac_liberal_percentage(self):
        """Calculate percentage of PAC liberal donations"""
        if not self.affiliated_pac_total_donations:
            return None
        return (self.affiliated_pac_liberal_total_donations or 0) / self.affiliated_pac_total_donations * 100

    @property
    def overall_conservative_percentage(self):
        """Calculate overall percentage of conservative donations across direct and PAC"""
        total = (self.direct_total_donations or 0) + (self.affiliated_pac_total_donations or 0)
        if not total:
            return None
        conservative_total = (self.direct_conservative_total_donations or 0) + (self.affiliated_pac_conservative_total_donations or 0)
        return conservative_total / total * 100

    @property
    def overall_liberal_percentage(self):
        """Calculate overall percentage of liberal donations across direct and PAC"""
        total = (self.direct_total_donations or 0) + (self.affiliated_pac_total_donations or 0)
        if not total:
            return None
        liberal_total = (self.direct_liberal_total_donations or 0) + (self.affiliated_pac_liberal_total_donations or 0)
        return liberal_total / total * 100

class ProductCategory(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='children'
    )
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
