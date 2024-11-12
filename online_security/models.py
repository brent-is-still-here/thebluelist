# online_security/models.py
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.db.models import F
from django.contrib.postgres.fields import ArrayField

def validate_platforms(value):
    valid_platforms = {'Mac', 'Windows', 'Linux', 'Android', 'iOS', 'Browser'}
    invalid_platforms = [platform for platform in value if platform not in valid_platforms]
    if invalid_platforms:
        raise ValidationError(
            f"Invalid platform(s): {', '.join(invalid_platforms)}. "
            f"Valid platforms are: {', '.join(valid_platforms)}"
        )

class OrderedModelMixin:
    def save(self, *args, **kwargs):
        if self._state.adding:  # If this is a new object
            last_order = self.__class__.objects.aggregate(
                models.Max('order'))['order__max']
            self.order = (last_order or 0) + 1
        super().save(*args, **kwargs)

    def update_order(self, new_order):
        if new_order == self.order:
            return

        with transaction.atomic():
            if new_order < self.order:
                # Moving up in the list
                self.__class__.objects.filter(
                    order__gte=new_order,
                    order__lt=self.order
                ).update(order=F('order') + 1)
            else:
                # Moving down in the list
                self.__class__.objects.filter(
                    order__gt=self.order,
                    order__lte=new_order
                ).update(order=F('order') - 1)
            
            self.order = new_order
            self.save()

class Category(OrderedModelMixin, models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    importance = models.CharField(
        max_length=20,
        choices=[
            ('critical', 'Critical'),
            ('recommended', 'Recommended'),
            ('optional', 'Optional')
        ]
    )
    order = models.IntegerField(default=0)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

class Recommendation(OrderedModelMixin, models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    importance = models.CharField(
        max_length=20,
        choices=[
            ('critical', 'Critical'),
            ('recommended', 'Recommended'),
            ('optional', 'Optional')
        ]
    )
    categories = models.ManyToManyField(Category, related_name='recommendations')
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

class Solution(OrderedModelMixin, models.Model):
    COST_DURATION_CHOICES = [
        ('monthly', 'Monthly'),
        ('annual', 'Annual'),
        ('lifetime', 'Lifetime'),
        ('one-time', 'One-time Purchase')
    ]

    DIFFICULTY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High')
    ]

    name = models.CharField(max_length=200)
    logo_icon = models.ImageField(upload_to='solution_logos/', null=True, blank=True)
    description = models.TextField()
    type = models.CharField(
        max_length=20,
        choices=[
            ('product', 'Product'),
            ('service', 'Service'),
            ('practice', 'Practice')
        ]
    )
    cost = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    cost_duration = models.CharField(
        max_length=20,
        choices=COST_DURATION_CHOICES,
        null=True,
        blank=True
    )
    implementation_difficulty = models.CharField(
        max_length=10,
        choices=DIFFICULTY_CHOICES,
        null=True, 
        blank=True
    )
    learning_curve = models.CharField(
        max_length=10,
        choices=DIFFICULTY_CHOICES,
        null=True, 
        blank=True
    )
    implementation_time = models.CharField(max_length=100, null=True, blank=True)
    supported_platforms = ArrayField(
        models.CharField(max_length=50),
        validators=[validate_platforms],
        null=True,
        blank=True
    )
    download_link = models.URLField(null=True, blank=True)
    recommendations = models.ManyToManyField(Recommendation, related_name='solutions')
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

class Tutorial(OrderedModelMixin, models.Model):
    solution = models.ForeignKey(Solution, on_delete=models.CASCADE, related_name='tutorials')
    name = models.CharField(max_length=200)
    description = models.TextField()
    estimated_time = models.CharField(max_length=100)
    difficulty = models.CharField(
        max_length=10,
        choices=Solution.DIFFICULTY_CHOICES
    )
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return f"{self.solution.name} - {self.name}"

class TutorialStep(OrderedModelMixin, models.Model):
    tutorial = models.ForeignKey(Tutorial, on_delete=models.CASCADE, related_name='steps')
    order = models.IntegerField()
    name = models.CharField(max_length=200)
    description = models.TextField()
    image_file = models.ImageField(upload_to='tutorial_images/', null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['tutorial', 'order']
        unique_together = ['tutorial', 'order']

    def __str__(self):
        return f"{self.tutorial.name} - Step {self.order}: {self.name}"