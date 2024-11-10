from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Case, IntegerField, Q, Value, When
from django.db.models.functions import Lower
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.text import slugify
from django.views.decorators.http import require_GET

from .models import (
    Business, 
    EditRequest, 
    PoliticalData, 
    ProductCategory, 
    ServiceCategory
)

@login_required
def add_business(request):
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
                    conservative_percentage=float(request.POST['conservative_percentage']),
                    conservative_total_donations=float(request.POST['conservative_total_donations']),
                    liberal_percentage=float(request.POST['liberal_percentage']),
                    liberal_total_donations=float(request.POST['liberal_total_donations']),
                    trump_donor=request.POST.get('trump_donor') == 'on',
                    america_pac_donor=request.POST.get('america_pac_donor') == 'on',
                    save_america_pac_donor=request.POST.get('save_america_pac_donor') == 'on',
                    data_source=request.POST['data_source']
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
                
                # Handle services if company provides them
                if business.provides_services:
                    services = request.POST.getlist('services')
                    business.services.set(services)
                
                # Handle products if company provides them
                if business.provides_products:
                    products = request.POST.getlist('products')
                    business.products.set(products)
                
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

def business_detail(request, slug):
    business = get_object_or_404(Business.objects.prefetch_related(
        'services', 
        'products', 
        'subsidiaries'
    ).select_related(
        'parent_company',
        'politicaldata'
    ), slug=slug)
    
    return render(request, 'companies/business_detail.html', {
        'business': business,
    })

def business_search(request):
    query = request.GET.get('q', '').strip()
    businesses = Business.objects.none()
    
    if query:
        # Create a query that checks for exact matches and partial matches
        # Use Case/When to assign priority values
        businesses = Business.objects.annotate(
            search_priority=Case(
                # Priority 1: Exact name match (case-insensitive)
                When(name__iexact=query, then=Value(3)),
                # Priority 2: Name contains the query
                When(name__icontains=query, then=Value(2)),
                # Priority 3: Description contains the query
                When(description__icontains=query, then=Value(1)),
                default=Value(0),
                output_field=IntegerField(),
            )
        ).filter(
            # Combine conditions with OR
            Q(name__icontains=query) |
            Q(description__icontains=query)
        ).select_related(
            'politicaldata'
        ).order_by(
            '-search_priority',  # Sort by priority (highest first)
            'name'              # Then alphabetically by name
        )
    
    return render(request, 'companies/business_search.html', {
        'query': query,
        'businesses': businesses,
    })

@login_required
def edit_requests(request):
    user_requests = EditRequest.objects.filter(submitted_by=request.user)
    return render(request, 'companies/edit_requests.html', {
        'edit_requests': user_requests
    })

@require_GET
def filter_categories(request):
    query = request.GET.get('q', '').strip().lower()
    category_type = request.GET.get('type')
    
    if category_type == 'services':
        categories = ServiceCategory.objects.filter(name__icontains=query).order_by('name')
    elif category_type == 'products':
        categories = ProductCategory.objects.filter(name__icontains=query).order_by('name')
    else:
        return JsonResponse({'error': 'Invalid category type'}, status=400)
    
    results = [{'id': cat.id, 'name': cat.name, 'description': cat.description} for cat in categories]
    return JsonResponse({'results': results})

def home(request):
    return render(request, 'companies/home.html')

@login_required
def submit_update(request, business_id):
    business = get_object_or_404(
        Business.objects.prefetch_related(
            'services',
            'products'
        ), 
        id=business_id
    )
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                edit_request = EditRequest.objects.create(
                    business=business,
                    submitted_by=request.user,
                    
                    # Business data changes
                    name=request.POST.get('name', ''),
                    description=request.POST.get('description', ''),
                    
                    # Service/Product provision changes
                    provides_services=request.POST.get('provides_services') == 'on' 
                        if 'provides_services' in request.POST else None,
                    provides_products=request.POST.get('provides_products') == 'on'
                        if 'provides_products' in request.POST else None,

                    # Political data changes
                    conservative_percentage=float(request.POST.get('conservative_percentage')) if request.POST.get('conservative_percentage') else None,
                    conservative_total_donations=float(request.POST.get('conservative_total_donations')) if request.POST.get('conservative_total_donations') else None,
                    liberal_percentage=float(request.POST.get('liberal_percentage')) if request.POST.get('liberal_percentage') else None,
                    liberal_total_donations=float(request.POST.get('liberal_total_donations')) if request.POST.get('liberal_total_donations') else None,
                    trump_donor=request.POST.get('trump_donor') == 'on',
                    america_pac_donor=request.POST.get('america_pac_donor') == 'on',
                    save_america_pac_donor=request.POST.get('save_america_pac_donor') == 'on',
                    data_source=request.POST.get('data_source', ''),
                    
                    # Update metadata
                    justification=request.POST['justification'],
                    supporting_links=request.POST.get('supporting_links', '')
                )

                # Handle services changes
                if 'services_to_add' in request.POST:
                    edit_request.services_to_add.set(request.POST.getlist('services_to_add'))
                if 'services_to_remove' in request.POST:
                    edit_request.services_to_remove.set(request.POST.getlist('services_to_remove'))
                
                # Handle products changes
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
                'available_services': ServiceCategory.objects.all(),  # Changed from services to available_services
                'available_products': ProductCategory.objects.all(),  # Changed from products to available_products
            })
    
    # For GET request, show form with current values
    political_data = getattr(business, 'politicaldata', None)
    initial_data = {
        'name': business.name,
        'description': business.description,
        'conservative_percentage': political_data.conservative_percentage if political_data else None,
        'conservative_total_donations': political_data.conservative_total_donations if political_data else None,
        'liberal_percentage': political_data.liberal_percentage if political_data else None,
        'liberal_total_donations': political_data.liberal_total_donations if political_data else None,
        'trump_donor': political_data.trump_donor if political_data else False,
        'america_pac_donor': political_data.america_pac_donor if political_data else False,
        'save_america_pac_donor': political_data.save_america_pac_donor if political_data else False,
        'data_source': political_data.data_source if political_data else '',
    }
    
    return render(request, 'companies/submit_update.html', {
        'business': business,
        'form_data': initial_data,
        'available_services': ServiceCategory.objects.all(),  # Changed from services to available_services
        'available_products': ProductCategory.objects.all(),  # Changed from products to available_products
    })
