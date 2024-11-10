from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Business, EditRequest, PoliticalData
from django.db import transaction

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
                    description=request.POST['description']
                )
                
                PoliticalData.objects.create(
                    business=business,
                    republican_percentage=float(request.POST['republican_percentage']),
                    democrat_percentage=float(request.POST['democrat_percentage']),
                    trump_donor=request.POST.get('trump_donor') == 'on',
                    america_pac_donor=request.POST.get('america_pac_donor') == 'on',
                    data_source=request.POST['data_source']
                )
                
                messages.success(request, 'Business added successfully!')
                return redirect('business_search')
        except Exception as e:
            messages.error(request, f'Error adding business: {str(e)}')
            return render(request, 'companies/add_business.html', {
                'error': str(e),
                # Return the submitted data so the form can be repopulated
                'form_data': request.POST
            })
            
    return render(request, 'companies/add_business.html')

@login_required
def edit_requests(request):
    user_requests = EditRequest.objects.filter(submitted_by=request.user)
    return render(request, 'companies/edit_requests.html', {
        'edit_requests': user_requests
    })