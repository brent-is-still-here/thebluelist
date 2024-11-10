from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.db import transaction
from django.db.models import Case, IntegerField, Q, Value, When
from django.db.models.functions import Lower
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
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

def is_reviewer(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)

@permission_required('companies.can_review_edits', raise_exception=True)
def review_edit_request(request, edit_request_id):
    edit_request = get_object_or_404(
        EditRequest.objects.select_related('business', 'submitted_by'),  # Changed this line
        id=edit_request_id
    )

    if request.method == 'POST':
        action = request.POST.get('action')
        if action in ['approve', 'reject']:
            with transaction.atomic():
                edit_request.status = 'approved' if action == 'approve' else 'rejected'
                edit_request.reviewed_by = request.user
                edit_request.reviewed_at = timezone.now()
                edit_request.review_notes = request.POST.get('review_notes', '')
                edit_request.save()
                
                if action == 'approve':
                    # Apply the changes to the business
                    business = edit_request.business
                    
                    # Update basic info
                    if edit_request.name:
                        business.name = edit_request.name
                    if edit_request.description:
                        business.description = edit_request.description
                    
                    # Update service/product flags
                    if edit_request.provides_services is not None:
                        business.provides_services = edit_request.provides_services
                    if edit_request.provides_products is not None:
                        business.provides_products = edit_request.provides_products
                    
                    business.save()
                    
                    # Update political data
                    political_data = business.politicaldata
                    for field in ['conservative_percentage', 'conservative_total_donations',
                                'liberal_percentage', 'liberal_total_donations',
                                'trump_donor', 'america_pac_donor', 'save_america_pac_donor',
                                'data_source']:
                        value = getattr(edit_request, field)
                        if value is not None:
                            setattr(political_data, field, value)
                    political_data.save()
                    
                    # Update services
                    if edit_request.services_to_add.exists():
                        business.services.add(*edit_request.services_to_add.all())
                    if edit_request.services_to_remove.exists():
                        business.services.remove(*edit_request.services_to_remove.all())
                    
                    # Update products
                    if edit_request.products_to_add.exists():
                        business.products.add(*edit_request.products_to_add.all())
                    if edit_request.products_to_remove.exists():
                        business.products.remove(*edit_request.products_to_remove.all())
                
                messages.success(request, f'Edit request {action}d successfully.')
                return redirect('review_edit_requests')
        pass

    # Prepare changes display
    changes = {}
    business = edit_request.business
    political_data = getattr(business, 'politicaldata', None)

    if edit_request.name:
        changes['Name'] = {
            'current': business.name,
            'proposed': edit_request.name
        }

    if edit_request.description:
        changes['Description'] = {
            'current': business.description,
            'proposed': edit_request.description
        }

    # Check political data changes
    political_fields = [
        ('conservative_percentage', 'Conservative Percentage'),
        ('conservative_total_donations', 'Conservative Total Donations'),
        ('liberal_percentage', 'Liberal Percentage'),
        ('liberal_total_donations', 'Liberal Total Donations'),
    ]

    if edit_request.description:
        changes['Description'] = {
            'current': business.description,
            'proposed': edit_request.description
        }

    # Check political data changes
    political_fields = [
        ('conservative_percentage', 'Conservative Percentage'),
        ('conservative_total_donations', 'Conservative Total Donations'),
        ('liberal_percentage', 'Liberal Percentage'),
        ('liberal_total_donations', 'Liberal Total Donations'),
    ]

    for field, label in political_fields:
        new_value = getattr(edit_request, field)
        if new_value is not None:
            current_value = getattr(political_data, field) if political_data else None
            changes[label] = {
                'current': f"{current_value:.2f}" if current_value is not None else "Not set",
                'proposed': f"{new_value:.2f}"
            }

    # Check boolean political fields
    boolean_fields = [
        ('trump_donor', 'Trump Donor'),
        ('america_pac_donor', 'America PAC Donor'),
        ('save_america_pac_donor', 'Save America PAC Donor'),
    ]

    for field, label in boolean_fields:
        new_value = getattr(edit_request, field)
        if new_value is not None:
            current_value = getattr(political_data, field) if political_data else False
            changes[label] = {
                'current': 'Yes' if current_value else 'No',
                'proposed': 'Yes' if new_value else 'No'
            }

    # Check data source changes
    if edit_request.data_source:
        changes['Data Source'] = {
            'current': political_data.data_source if political_data else '',
            'proposed': edit_request.data_source
        }

    # Check service changes
    if edit_request.services_to_add.exists():
        services_to_add = edit_request.services_to_add.all()
        changes['Services to Add'] = {
            'current': 'None',
            'proposed': ', '.join(s.name for s in services_to_add)
        }

    if edit_request.services_to_remove.exists():
        services_to_remove = edit_request.services_to_remove.all()
        changes['Services to Remove'] = {
            'current': ', '.join(s.name for s in services_to_remove),
            'proposed': 'Will be removed'
        }

    # Check product changes
    if edit_request.products_to_add.exists():
        products_to_add = edit_request.products_to_add.all()
        changes['Products to Add'] = {
            'current': 'None',
            'proposed': ', '.join(p.name for p in products_to_add)
        }

    if edit_request.products_to_remove.exists():
        products_to_remove = edit_request.products_to_remove.all()
        changes['Products to Remove'] = {
            'current': ', '.join(p.name for p in products_to_remove),
            'proposed': 'Will be removed'
        }

    # Check service/product provision changes
    if edit_request.provides_services is not None:
        changes['Provides Services'] = {
            'current': 'Yes' if business.provides_services else 'No',
            'proposed': 'Yes' if edit_request.provides_services else 'No'
        }

    if edit_request.provides_products is not None:
        changes['Provides Products'] = {
            'current': 'Yes' if business.provides_products else 'No',
            'proposed': 'Yes' if edit_request.provides_products else 'No'
        }
    
    return render(request, 'companies/review_edit_request.html', {
        'edit_request': edit_request,
        'changes': changes,
    })

@permission_required('companies.can_review_edits', raise_exception=True)
def review_edit_requests(request):
    # Get filters
    status = request.GET.get('status', 'pending')
    business_filter = request.GET.get('business', '')
    
    # Build queryset
    edit_requests = EditRequest.objects.select_related('business', 'submitted_by').order_by('-created_at')
    
    if status:
        edit_requests = edit_requests.filter(status=status)
    if business_filter:
        edit_requests = edit_requests.filter(business__name__icontains=business_filter)
    
    return render(request, 'companies/review_edit_requests.html', {
        'edit_requests': edit_requests,
        'status': status,
        'business_filter': business_filter,
    })

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
