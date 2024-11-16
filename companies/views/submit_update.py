from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from companies.models import (
    Business,
    DataSource,
    EditRequest,
    ProductCategory, 
    ServiceCategory
)

@login_required
def submit_update(request, business_id):
    business = get_object_or_404(Business.objects.prefetch_related('services', 'products'), id=business_id)
    
    def safe_float(value, default=0.0):
        """Convert string to float, returning default if empty or invalid"""
        try:
            return float(value) if value else default
        except ValueError:
            return default

    if request.method == 'POST':
        try:
            with transaction.atomic():
                edit_request = EditRequest.objects.create(
                    business=business,
                    submitted_by=request.user,
                    name=request.POST.get('name', ''),
                    description=request.POST.get('description', ''),
                    provides_services='provides_services' in request.POST,
                    provides_products='provides_products' in request.POST,

                    # Direct donations
                    direct_conservative_total_donations=safe_float(request.POST.get('direct_conservative_total_donations')),
                    direct_liberal_total_donations=safe_float(request.POST.get('direct_liberal_total_donations')),
                    direct_total_donations=safe_float(request.POST.get('direct_total_donations')),
                    direct_america_pac_donor=request.POST.get('direct_america_pac_donor') == 'on',
                    direct_save_america_pac_donor=request.POST.get('direct_save_america_pac_donor') == 'on',
                    
                    # PAC donations
                    affiliated_pac_conservative_total_donations=safe_float(request.POST.get('affiliated_pac_conservative_total_donations')),
                    affiliated_pac_liberal_total_donations=safe_float(request.POST.get('affiliated_pac_liberal_total_donations')),
                    affiliated_pac_total_donations=safe_float(request.POST.get('affiliated_pac_total_donations')),
                    affiliated_pac_america_pac_donor=request.POST.get('affiliated_pac_america_pac_donor') == 'on',
                    affiliated_pac_save_america_pac_donor=request.POST.get('affiliated_pac_save_america_pac_donor') == 'on',
                    
                    # Senior employee donations
                    senior_employee_conservative_total_donations=safe_float(request.POST.get('senior_employee_conservative_total_donations')),
                    senior_employee_liberal_total_donations=safe_float(request.POST.get('senior_employee_liberal_total_donations')),
                    senior_employee_total_donations=safe_float(request.POST.get('senior_employee_total_donations')),
                    senior_employee_trump_donor=request.POST.get('senior_employee_trump_donor') == 'on',
                    senior_employee_america_pac_donor=request.POST.get('senior_employee_america_pac_donor') == 'on',
                    senior_employee_save_america_pac_donor=request.POST.get('senior_employee_save_america_pac_donor') == 'on',
                    
                    justification=request.POST['justification'],
                    supporting_links=request.POST.get('supporting_links', '')
                )

                # Handle new data sources
                data_sources = request.POST.getlist('new_data_sources[]')
                for source_url in data_sources:
                    if source_url:
                        DataSource.objects.get_or_create(
                            business=business,
                            url=source_url,
                            defaults={
                                'reason': 'update',
                                'is_approved': False,
                                'edit_request': edit_request
                            }
                        )

                # Handle services/products changes
                if 'services_to_add' in request.POST:
                    edit_request.services_to_add.set(request.POST.getlist('services_to_add'))
                if 'services_to_remove' in request.POST:
                    edit_request.services_to_remove.set(request.POST.getlist('services_to_remove'))
                if 'products_to_add' in request.POST:
                    edit_request.products_to_add.set(request.POST.getlist('products_to_add'))
                if 'products_to_remove' in request.POST:
                    edit_request.products_to_remove.set(request.POST.getlist('products_to_remove'))
                
                messages.success(request, 'Update request submitted successfully! It will be reviewed by our team.')
                return redirect('business_search')
                
        except Exception as e:
            messages.error(request, f'Error submitting update: {str(e)}')
            return render(request, 'companies/submit_update.html', {
                'error': str(e),
                'business': business,
                'form_data': request.POST,
                'available_services': ServiceCategory.objects.all(),
                'available_products': ProductCategory.objects.all(),
            })
    
    # For GET request, show form with current values
    political_data = getattr(business, 'politicaldata', None)
    initial_data = {
        'name': business.name,
        'description': business.description,
        'provides_services': business.provides_services,
        'provides_products': business.provides_products,
    }
    
    return render(request, 'companies/submit_update.html', {
        'business': business,
        'form_data': initial_data,
        'political_data': political_data,
        'available_services': ServiceCategory.objects.all(),
        'available_products': ProductCategory.objects.all(),
        'current_data_sources': business.data_sources.all().order_by('-created_at')
    })
