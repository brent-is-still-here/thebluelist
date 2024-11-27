# Generated by Django 5.1.3 on 2024-11-18 23:01

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('slug', models.SlugField(max_length=100, unique=True)),
                ('currency', models.CharField(max_length=50)),
                ('capital_city', models.CharField(max_length=100)),
                ('population', models.PositiveIntegerField()),
                ('timezone', models.CharField(max_length=50)),
                ('avg_cost_of_living', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('avg_house_cost', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('avg_rent_cost', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_created', to=settings.AUTH_USER_MODEL)),
                ('last_modified_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_modified', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'countries',
            },
        ),
        migrations.CreateModel(
            name='CostOfLiving',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('city', models.CharField(max_length=100)),
                ('date_recorded', models.DateField()),
                ('rent_1bed_city', models.DecimalField(decimal_places=2, max_digits=10)),
                ('rent_3bed_city', models.DecimalField(decimal_places=2, max_digits=10)),
                ('rent_1bed_suburban', models.DecimalField(decimal_places=2, max_digits=10)),
                ('rent_3bed_suburban', models.DecimalField(decimal_places=2, max_digits=10)),
                ('utilities', models.DecimalField(decimal_places=2, max_digits=8)),
                ('internet', models.DecimalField(decimal_places=2, max_digits=8)),
                ('groceries', models.DecimalField(decimal_places=2, max_digits=8)),
                ('transportation', models.DecimalField(decimal_places=2, max_digits=8)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_created', to=settings.AUTH_USER_MODEL)),
                ('last_modified_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_modified', to=settings.AUTH_USER_MODEL)),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='relocation_planner.country')),
            ],
            options={
                'verbose_name_plural': 'costs of living',
            },
        ),
        migrations.CreateModel(
            name='CitizenshipProcess',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('residence_requirement_years', models.PositiveIntegerField()),
                ('language_requirement', models.TextField()),
                ('dual_citizenship_allowed', models.BooleanField()),
                ('test_required', models.BooleanField()),
                ('test_details', models.TextField(blank=True)),
                ('cost', models.DecimalField(decimal_places=2, max_digits=10)),
                ('process_details', models.TextField()),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_created', to=settings.AUTH_USER_MODEL)),
                ('last_modified_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_modified', to=settings.AUTH_USER_MODEL)),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='relocation_planner.country')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='EditHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('object_id', models.PositiveIntegerField()),
                ('field_name', models.CharField(max_length=100)),
                ('old_value', models.TextField(blank=True)),
                ('new_value', models.TextField(blank=True)),
                ('change_reason', models.TextField()),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_created', to=settings.AUTH_USER_MODEL)),
                ('last_modified_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_modified', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='HealthcareInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('has_universal_healthcare', models.BooleanField()),
                ('immigrant_coverage_waiting_period', models.CharField(max_length=100)),
                ('private_insurance_requirement', models.TextField()),
                ('avg_cost_private_insurance', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('healthcare_system_details', models.TextField()),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='relocation_planner.country')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_created', to=settings.AUTH_USER_MODEL)),
                ('last_modified_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_modified', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=50, unique=True)),
                ('code', models.CharField(max_length=10, unique=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_created', to=settings.AUTH_USER_MODEL)),
                ('last_modified_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_modified', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='country',
            name='business_language',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='business_countries', to='relocation_planner.language'),
        ),
        migrations.AddField(
            model_name='country',
            name='official_languages',
            field=models.ManyToManyField(related_name='countries', to='relocation_planner.language'),
        ),
        migrations.CreateModel(
            name='PetRelocationRequirement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('pet_type', models.CharField(max_length=50)),
                ('quarantine_required', models.BooleanField()),
                ('quarantine_duration', models.CharField(blank=True, max_length=50)),
                ('vaccination_requirements', models.TextField()),
                ('documentation_required', models.TextField()),
                ('restrictions', models.TextField(blank=True)),
                ('estimated_cost', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='relocation_planner.country')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_created', to=settings.AUTH_USER_MODEL)),
                ('last_modified_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_modified', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PropertyCost',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('city', models.CharField(max_length=100)),
                ('date_recorded', models.DateField()),
                ('property_type', models.CharField(choices=[('APARTMENT', 'Apartment'), ('HOUSE', 'House'), ('LAND', 'Land')], max_length=50)),
                ('size_sqm', models.DecimalField(decimal_places=2, max_digits=8)),
                ('price', models.DecimalField(decimal_places=2, max_digits=12)),
                ('location_type', models.CharField(choices=[('CITY_CENTER', 'City Center'), ('SUBURBAN', 'Suburban'), ('RURAL', 'Rural')], max_length=20)),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='relocation_planner.country')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_created', to=settings.AUTH_USER_MODEL)),
                ('last_modified_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_modified', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ResourceLink',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=200)),
                ('url', models.URLField()),
                ('category', models.CharField(choices=[('OFFICIAL', 'Official Government Resource'), ('HEALTHCARE', 'Healthcare Information'), ('HOUSING', 'Housing Information'), ('EDUCATION', 'Education Information'), ('VISA', 'Visa Information'), ('EMPLOYMENT', 'Employment Information'), ('COMMUNITY', 'Community Resource')], max_length=50)),
                ('description', models.TextField()),
                ('is_verified', models.BooleanField(default=False)),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='relocation_planner.country')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_created', to=settings.AUTH_USER_MODEL)),
                ('last_modified_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_modified', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='UserExperience',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=200)),
                ('content', models.TextField()),
                ('moved_from', models.CharField(max_length=100)),
                ('year_moved', models.PositiveIntegerField()),
                ('current_status', models.CharField(choices=[('PLANNING', 'Planning Stage'), ('IN_PROGRESS', 'Currently Relocating'), ('RELOCATED', 'Successfully Relocated'), ('RETURNED', 'Returned to Origin')], max_length=50)),
                ('would_recommend', models.BooleanField()),
                ('challenges_faced', models.TextField()),
                ('tips', models.TextField()),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='relocation_planner.country')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_created', to=settings.AUTH_USER_MODEL)),
                ('last_modified_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_modified', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='VisaType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('duration', models.CharField(max_length=50)),
                ('processing_time', models.CharField(max_length=50)),
                ('allows_family', models.BooleanField()),
                ('family_notes', models.TextField(blank=True)),
                ('can_work', models.BooleanField()),
                ('path_to_citizenship', models.BooleanField()),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='relocation_planner.country')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_created', to=settings.AUTH_USER_MODEL)),
                ('last_modified_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_modified', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('country', 'name')},
            },
        ),
        migrations.CreateModel(
            name='VisaRequirement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('requirement', models.CharField(max_length=255)),
                ('details', models.TextField()),
                ('is_mandatory', models.BooleanField(default=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_created', to=settings.AUTH_USER_MODEL)),
                ('last_modified_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_modified', to=settings.AUTH_USER_MODEL)),
                ('visa_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='relocation_planner.visatype')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('category', models.CharField(choices=[('SAFETY', 'Safety'), ('HEALTHCARE', 'Healthcare Quality'), ('EDUCATION', 'Education Quality'), ('HAPPINESS', 'Overall Happiness'), ('INFRASTRUCTURE', 'Infrastructure'), ('FOREIGNER_FRIENDLY', 'Foreigner Friendliness'), ('WORK_LIFE', 'Work-Life Balance'), ('ENVIRONMENT', 'Environmental Quality')], max_length=50)),
                ('score', models.IntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ('comment', models.TextField(blank=True)),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='relocation_planner.country')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_created', to=settings.AUTH_USER_MODEL)),
                ('last_modified_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_modified', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('country', 'user', 'category')},
            },
        ),
        migrations.CreateModel(
            name='RelocationProcess',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('step_number', models.PositiveIntegerField()),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('estimated_time', models.CharField(max_length=50)),
                ('estimated_cost', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('required_documents', models.TextField()),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='relocation_planner.country')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_created', to=settings.AUTH_USER_MODEL)),
                ('last_modified_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_modified', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['step_number'],
                'unique_together': {('country', 'step_number')},
            },
        ),
    ]