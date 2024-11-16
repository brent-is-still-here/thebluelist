from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from companies.models import (
    EditRequest
)


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

                    # approve the data source
                    edit_request.data_sources.all().update(is_approved=True)
                    
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
