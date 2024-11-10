from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.text import slugify
from django.db import transaction
from .models import Business, EditRequest, PoliticalData, ServiceCategory, ProductCategory

def home(request):
    return render(request, 'companies/home.html')

def business_search(request):
    query = request.GET.get('q', '')
    businesses = Business.objects.filter(name__icontains=query) if query else Business.objects.none()
    return render(request, 'companies/business_search.html', {
        'query': query,
        'businesses': businesses
    })

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

@login_required
def edit_requests(request):
    user_requests = EditRequest.objects.filter(submitted_by=request.user)
    return render(request, 'companies/edit_requests.html', {
        'edit_requests': user_requests
    })