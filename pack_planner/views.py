from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.decorators.http import require_http_methods
from django.views.generic.edit import FormView

import json

from pack_planner.forms import AssessmentForm, DataUploadForm
from pack_planner.models import Category, Item, Product
from pack_planner.services.data_processor import DataProcessor, generate_packs

@login_required
@permission_required('pack_planner.pack_planner_data_upload_permission', raise_exception=True)
def data_upload(request):
    """Handle data uploads for pack planner"""
    if request.method == 'POST':
        form = DataUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                file = form.cleaned_data['file']
                upload_type = form.cleaned_data['upload_type']
                data = json.load(file)
                
                with transaction.atomic():
                    processor = DataProcessor(upload_type)
                    result = processor.process_data(data)
                    
                    messages.success(
                        request,
                        f'Successfully processed data: {result["categories"]} categories, '
                        f'{result["items"]} items, {result["products"]} products'
                    )
                    
                return redirect('pack_upload')
            except Exception as e:
                messages.error(request, f'Error processing file: {str(e)}')
    else:
        form = DataUploadForm()
    
    return render(request, 'pack_planner/data_upload.html', {
        'form': form
    })

def item_detail(request, pk):
    """Detailed view of an item with alternatives and products"""
    item = get_object_or_404(
        Item.objects.prefetch_related(
            'alternatives',
            'recommended_products'
        ),
        pk=pk
    )
    
    context = {
        'item': item,
    }
    return render(request, 'pack_planner/item_detail.html', context)

def pack_landing(request):
    """Landing page with overview of packing preparation"""
    critical_categories = Category.objects.prefetch_related('items').filter(importance='critical')
    
    context = {
        'critical_categories': critical_categories,
        'has_upload_permission': request.user.is_authenticated and
            request.user.has_perm('pack_planner.pack_planner_data_upload_permission')
    }
    return render(request, 'pack_planner/landing.html', context)

def pack_assessment(request):
    """
    View for displaying the pack assessment form and saving user inputs to the session.
    """
    if request.method == 'POST':
        form_data = {
            'adults': int(request.POST.get('adults', 1)),
            'children': int(request.POST.get('children', 0)),
            'hasElderly': request.POST.get('hasElderly') == 'on',
            'hasDisabled': request.POST.get('hasDisabled') == 'on',
            'hasPets': request.POST.get('hasPets') == 'on',
            'petTypes': request.POST.getlist('petTypes'),
            'transportType': request.POST.get('transportType', 'walking')
        }
        
        # Store the assessment data in the session
        request.session['pack_assessment'] = form_data
        return redirect('pack_assessment_results')
    
    return render(request, 'pack_planner/assessment.html')

def pack_assessment_results(request):
    """
    Display personalized packing recommendations based on assessment.
    """
    assessment_data = request.session.get('pack_assessment')
    if not assessment_data:
        messages.error(request, 'Please complete the pack assessment first.')
        return redirect('pack_assessment')

    # Generate recommendations
    recommendations = generate_packs(assessment_data)
    
    context = {
        'assessment': assessment_data,
        'recommendations': recommendations
    }
    
    return render(request, 'pack_planner/assessment_results.html', context)

def pack_browse(request):
    """Browse all packing recommendations with filtering"""
    # Get filter parameters
    query = request.GET.get('q', '').strip()
    category_id = request.GET.get('category')
    importance = request.GET.get('importance')
    special_need = request.GET.get('special_need')
    
    # Start with all items
    items = Item.objects.all()
    
    # Apply filters
    if query:
        items = items.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(uses__icontains=query)
        )
    
    if category_id:
        items = items.filter(category_id=category_id)
    
    if importance:
        items = items.filter(importance=importance)
    
    if special_need:
        items = items.filter(special_considerations__icontains=special_need)
    
    # Get categories for filter dropdown
    categories = Category.objects.all()
    
    context = {
        'items': items,
        'categories': categories,
        'current_filters': {
            'query': query,
            'category': category_id,
            'importance': importance,
            'special_need': special_need,
        }
    }
    return render(request, 'pack_planner/browse.html', context)

def print_checklist(request):
    """Generate printable checklist of items"""
    assessment_data = request.session.get('pack_assessment')
    checklist = request.session.get('pack_checklist', {})
    
    items = Item.objects.filter(importance='critical')
    
    # Add additional items based on assessment
    if assessment_data:
        if assessment_data.get('children'):
            items = items.union(
                Item.objects.filter(special_considerations__icontains='children')
            )
        if assessment_data.get('has_elderly'):
            items = items.union(
                Item.objects.filter(special_considerations__icontains='elderly')
            )
        if assessment_data.get('has_pets'):
            items = items.union(
                Item.objects.filter(special_considerations__icontains='pets')
            )
    
    context = {
        'items': items,
        'checklist': checklist,
        'assessment': assessment_data,
    }
    return render(request, 'pack_planner/print_checklist.html', context)

@require_http_methods(["POST"])
def update_item_status(request):
    """Handle AJAX updates for item status (packed/not applicable)"""
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            item_id = request.POST.get('item_id')
            status = request.POST.get('status')
            
            if not item_id or not status:
                return JsonResponse({'status': 'error', 'message': 'Missing required fields'}, status=400)
            
            # Get or create checklist in session
            checklist = request.session.get('pack_checklist', {})
            checklist[str(item_id)] = status
            request.session['pack_checklist'] = checklist
            request.session.modified = True
            
            return JsonResponse({
                'status': 'success',
                'message': f'Item {item_id} marked as {status}'
            })
            
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
            
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)
    