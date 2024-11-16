from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import redirect, render
from companies.models import (
    Business,
    DataSource,
    PoliticalData, 
    ProductCategory, 
    ServiceCategory
)

@login_required
def add_business(request):
    if request.method == 'GET' and request.user.has_perm('companies.can_import_business_csv'):
        return render(request, 'companies/add_business.html', {
            'can_import_csv': True,
            'services': ServiceCategory.objects.all(),
            'products': ProductCategory.objects.all(),
        })
    
    def safe_float(value, default=0.0):
        """Convert string to float, returning default if empty or invalid"""
        try:
            return float(value) if value else default
        except ValueError:
            return default
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                business = Business.objects.create(
                    name=request.POST['name'],
                    website=request.POST['website'],
                    description=request.POST['description'],
                    provides_services=request.POST.get('provides_services') == 'on',
                    provides_products=request.POST.get('provides_products') == 'on',
                )
                
                # Create the political data
                PoliticalData.objects.create(
                    business=business,
                    # Direct donations
                    direct_conservative_total_donations=safe_float(request.POST.get('direct_conservative_total_donations', 0)),
                    direct_liberal_total_donations=safe_float(request.POST.get('direct_liberal_total_donations', 0)),
                    direct_total_donations=safe_float(request.POST.get('direct_total_donations', 0)),
                    direct_america_pac_donor=request.POST.get('direct_america_pac_donor') == 'on',
                    direct_save_america_pac_donor=request.POST.get('direct_save_america_pac_donor') == 'on',
                    
                    # PAC donations
                    affiliated_pac_conservative_total_donations=safe_float(request.POST.get('affiliated_pac_conservative_total_donations', 0)),
                    affiliated_pac_liberal_total_donations=safe_float(request.POST.get('affiliated_pac_liberal_total_donations', 0)),
                    affiliated_pac_total_donations=safe_float(request.POST.get('affiliated_pac_total_donations', 0)),
                    affiliated_pac_america_pac_donor=request.POST.get('affiliated_pac_america_pac_donor') == 'on',
                    affiliated_pac_save_america_pac_donor=request.POST.get('affiliated_pac_save_america_pac_donor') == 'on',
                    
                    # Senior employee donations
                    senior_employee_conservative_total_donations=safe_float(request.POST.get('senior_employee_conservative_total_donations', 0)),
                    senior_employee_liberal_total_donations=safe_float(request.POST.get('senior_employee_liberal_total_donations', 0)),
                    senior_employee_total_donations=safe_float(request.POST.get('senior_employee_total_donations', 0)),
                    senior_employee_trump_donor=request.POST.get('senior_employee_trump_donor') == 'on',
                    senior_employee_america_pac_donor=request.POST.get('senior_employee_america_pac_donor') == 'on',
                    senior_employee_save_america_pac_donor=request.POST.get('senior_employee_save_america_pac_donor') == 'on',
                )

                # Handle data sources
                form_data = {
                    'data_sources': request.POST.getlist('data_sources[]'),
                }

                # Create the data source records
                for source_url in form_data['data_sources']:
                    if source_url:
                        DataSource.objects.get_or_create(
                            business=business,
                            url=source_url,
                            defaults={
                                'reason': 'manual_addition',
                                'is_approved': True
                            }
                        )
                
                # Handle parent company if specified
                parent_name = request.POST.get('parent_company')
                if parent_name:
                    parent, created = Business.objects.get_or_create(
                        name=parent_name,
                        defaults={'description': f'Parent company of {business.name}'}
                    )
                    business.parent_company = parent
                    business.save()
                
                # Handle services and products
                if business.provides_services:
                    business.services.set(request.POST.getlist('services'))
                if business.provides_products:
                    business.products.set(request.POST.getlist('products'))
                
                messages.success(request, 'Business added successfully!')
                return redirect('business_search')

        except Exception as e:
            messages.error(request, f'Error adding business: {str(e)}')
            return render(request, 'companies/add_business.html', {
                'error': str(e),
                'form_data': request.POST,
                'services': ServiceCategory.objects.all(),
                'products': ProductCategory.objects.all(),
            })
            
    return render(request, 'companies/add_business.html', {
        'services': ServiceCategory.objects.all(),
        'products': ProductCategory.objects.all(),
    })
