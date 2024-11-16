from django.shortcuts import get_object_or_404, render
from companies.models import (
    Business
)


def business_detail(request, slug):
    business = get_object_or_404(
        Business.objects.prefetch_related(
            'services',
            'products',
            'subsidiaries'
        ).select_related(
            'parent_company',
            'politicaldata'  # Add this
        ),
        slug=slug
    )

    # Get a list of approved data sources
    approved_sources = business.data_sources.filter(is_approved=True)
    
    # Get alternative businesses
    alternatives = business.get_alternative_businesses(limit=5)
    
    # Check if there is any political data to display
    has_direct_donations = (
        business.politicaldata and 
        (business.politicaldata.direct_conservative_total_donations or 
         business.politicaldata.direct_liberal_total_donations)
    )
    
    has_pac_donations = (
        business.politicaldata and
        (business.politicaldata.affiliated_pac_conservative_total_donations or 
         business.politicaldata.affiliated_pac_liberal_total_donations)
    )

    has_senior_employee_donations = (
        business.politicaldata and
        (business.politicaldata.senior_employee_trump_donor or
         business.politicaldata.senior_employee_america_pac_donor or
         business.politicaldata.senior_employee_save_america_pac_donor)
    )
    
    return render(request, 'companies/business_detail.html', {
        'business': business,
        'approved_sources': approved_sources,
        'alternatives': alternatives,
        'has_direct_donations': has_direct_donations,
        'has_pac_donations': has_pac_donations,
        'has_senior_employee_donations': has_senior_employee_donations
    })

