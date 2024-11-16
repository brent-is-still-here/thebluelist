from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db import transaction
from django.shortcuts import redirect, render
from django.utils import timezone
from io import TextIOWrapper
from companies.models import (
    Business,
    CSVImportRateLimit,
    DataSource,
    PoliticalData, 
    ProductCategory, 
    ServiceCategory
)
import csv

@login_required
@permission_required('companies.can_import_business_csv')
def import_business(request):
    if request.method == 'POST':
        if not CSVImportRateLimit.can_import(request.user):
            messages.error(request, 'Please wait 30 seconds between imports.')
            return redirect('import_business')

        form_data = {
            'name': request.POST.get('name'),
            'website': request.POST.get('website'),
            'description': request.POST.get('description'),
            'data_sources': request.POST.getlist('data_sources[]'),
            'provides_services': request.POST.get('provides_services') == 'on',
            'provides_products': request.POST.get('provides_products') == 'on',
            'services': request.POST.getlist('services'),
            'products': request.POST.getlist('products'),
        }

        # Validate file extension
        csv_file = request.FILES.get('csv_file')
        if not csv_file or not csv_file.name.endswith('.csv'):
            messages.error(request, 'Please upload a valid CSV file.')
            return render(request, 'companies/import_business.html', {
                'services': ServiceCategory.objects.all(),
                'products': ProductCategory.objects.all(),
                'form_data': form_data
            })

        try:
            with transaction.atomic():
                # Create business first
                business = Business.objects.create(
                    name=form_data['name'],
                    website=form_data['website'],
                    description=form_data['description'],
                    provides_services=form_data['provides_services'],
                    provides_products=form_data['provides_products'],
                )

                if form_data['provides_services']:
                    business.services.set(form_data['services'])
                if form_data['provides_products']:
                    business.products.set(form_data['products'])

                # Process CSV
                csv_text = TextIOWrapper(csv_file, encoding='utf-8')
                reader = csv.DictReader(csv_text)
                
                # Validate CSV structure    
                required_fields = {'Recipient', 'View'}
                if not required_fields.issubset(reader.fieldnames):
                    raise ValueError('CSV file missing required columns')

                # At least one donation type column must exist
                if 'From Organization' not in reader.fieldnames and 'From Individuals' not in reader.fieldnames and 'From PACs' not in reader.fieldnames:
                    raise ValueError('CSV must contain at least one of "From Organization","From Individuals", or "From PACs" columns')
                
                # At least one data source is required
                if not form_data['data_sources']:
                    raise ValueError('At least one data source URL is required')

                if not any(url.strip() for url in form_data['data_sources']):
                    raise ValueError('At least one non-empty data source URL is required')

                # Initialize all counters and flags
                direct_liberal_total = Decimal('0')
                direct_conservative_total = Decimal('0')
                direct_total = Decimal('0')
                pac_liberal_total = Decimal('0')
                pac_conservative_total = Decimal('0')
                pac_total = Decimal('0')
                senior_employee_liberal_total = Decimal('0')
                senior_employee_conservative_total = Decimal('0')
                senior_employee_total = Decimal('0')
                
                direct_america_pac = False
                direct_save_america = False
                direct_maga_inc = False
                pac_america_pac = False
                pac_save_america = False
                pac_maga_inc = False
                senior_employee_america_pac = False
                senior_employee_save_america = False
                senior_employee_maga_inc = False
                senior_employee_trump_donor = False

                for row in reader:
                    view = row['View'].lower()
                    is_liberal = 'democrat' in view or 'liberal' in view
                    is_conservative = 'republican' in view or 'conservative' in view

                    # Process direct donations
                    if 'From Organization' in reader.fieldnames:
                        org_amount = Decimal(row['From Organization'].replace('$', '').replace(',', '') or '0')
                        recipient = row['Recipient'].lower()
                        if org_amount > 0:
                            if is_liberal:
                                direct_liberal_total += org_amount
                            elif is_conservative:
                                direct_conservative_total += org_amount
                            direct_total += org_amount

                            # Check specific donations
                            if 'america pac \(texas\)' in recipient:
                                direct_america_pac = True
                            elif 'save america' in recipient:
                                direct_save_america = True
                            elif 'make america great again inc' in recipient:
                                direct_maga_inc = True
                            
                    # Process PAC donations 
                    if 'From PACs' in reader.fieldnames:
                        pac_amount = Decimal(row['From PACs'].replace('$', '').replace(',', '') or '0')
                        recipient = row['Recipient'].lower()
                        if pac_amount > 0:
                            if is_liberal:
                                pac_liberal_total += pac_amount
                            elif is_conservative:
                                pac_conservative_total += pac_amount
                            pac_total += pac_amount

                            # Check specific donations
                            if 'trump' in recipient:
                                pac_trump_donor = True
                            elif 'america pac \(texas\)' in recipient:
                                pac_america_pac = True
                            elif 'save america' in recipient:
                                pac_save_america = True
                            elif 'make america great again inc' in recipient:
                                pac_maga_inc = True

                    # Process senior employee donations
                    if 'From Individuals' in reader.fieldnames:
                        individual_amount = Decimal(row['From Individuals'].replace('$', '').replace(',', '') or '0')
                        recipient = row['Recipient'].lower()
                        if individual_amount > 0:
                            if is_liberal:
                                senior_employee_liberal_total += individual_amount
                            elif is_conservative:
                                senior_employee_conservative_total += individual_amount
                            senior_employee_total += individual_amount

                            # Check specific donations
                            if 'trump' in recipient:
                                senior_employee_trump_donor = True
                            elif 'america pac \(texas\)' in recipient:
                                senior_employee_america_pac = True
                            elif 'save america' in recipient:
                                senior_employee_save_america = True
                            elif 'make america great again inc' in recipient:
                                senior_employee_maga_inc = True

                # Create political data
                PoliticalData.objects.create(
                    business=business,
                    # Direct donations
                    direct_conservative_total_donations=direct_conservative_total,
                    direct_liberal_total_donations=direct_liberal_total,
                    direct_total_donations=direct_total,
                    direct_america_pac_donor=direct_america_pac,
                    direct_save_america_pac_donor=direct_save_america,
                    direct_maga_inc_donor=direct_maga_inc,
                    
                    # PAC donations
                    affiliated_pac_conservative_total_donations=pac_conservative_total,
                    affiliated_pac_liberal_total_donations=pac_liberal_total,
                    affiliated_pac_total_donations=pac_total,
                    affiliated_pac_america_pac_donor=pac_america_pac,
                    affiliated_pac_save_america_pac_donor=pac_save_america,
                    affiliated_pac_maga_inc_donor=pac_maga_inc,
                    
                    # senior_employee donations - only setting Trump donor for now
                    senior_employee_conservative_total_donations=senior_employee_conservative_total,
                    senior_employee_liberal_total_donations=senior_employee_liberal_total,
                    senior_employee_total_donations=senior_employee_total,
                    senior_employee_trump_donor=senior_employee_trump_donor,
                    senior_employee_america_pac_donor=senior_employee_america_pac,
                    senior_employee_save_america_pac_donor=senior_employee_save_america,
                    senior_employee_maga_inc_donor=senior_employee_maga_inc,
                )

                # Create the data source records
                for source_url in form_data['data_sources']:
                    if source_url:
                        DataSource.objects.get_or_create(
                            business=business,
                            url=source_url,
                            defaults={
                                'reason': 'import',
                                'is_approved': True
                            }
                        )

                # Update rate limit
                CSVImportRateLimit.objects.update_or_create(
                    user=request.user,
                    defaults={'last_import_attempt': timezone.now()}
                )

                messages.success(request, 'Business imported successfully!')
                return redirect('business_detail', slug=business.slug)

        except Exception as e:
            messages.error(request, f'Error importing business: {str(e)}')
            return render(request, 'companies/import_business.html', {
                'services': ServiceCategory.objects.all(),
                'products': ProductCategory.objects.all(),
                'form_data': form_data
            })

    return render(request, 'companies/import_business.html', {
        'services': ServiceCategory.objects.all(),
        'products': ProductCategory.objects.all(),
    })
