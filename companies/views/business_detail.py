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
            'politicaldata'
        ),
        slug=slug
    )

    # Get political data (either direct or inherited)
    political_data, inherited_from = business.get_political_data()

    # Get a list of approved data sources
    approved_sources = business.data_sources.filter(is_approved=True)
    
    # Get alternative businesses
    alternatives = business.get_alternative_businesses(limit=5)
    
    # Check if there is any political data to display
    has_direct_donations = (
        political_data and 
        (political_data.direct_conservative_total_donations or 
         political_data.direct_liberal_total_donations)
    )
    
    has_pac_donations = (
        political_data and
        (political_data.affiliated_pac_conservative_total_donations or 
         political_data.affiliated_pac_liberal_total_donations)
    )

    has_senior_employee_donations = (
        political_data and
        (political_data.senior_employee_trump_donor or
         political_data.senior_employee_america_pac_donor or
         political_data.senior_employee_save_america_pac_donor)
    )
    
    return render(request, 'companies/business_detail.html', {
        'business': business,
        'political_data': political_data,
        'inherited_from': inherited_from,
        'approved_sources': approved_sources,
        'alternatives': alternatives,
        'has_direct_donations': has_direct_donations,
        'has_pac_donations': has_pac_donations,
        'has_senior_employee_donations': has_senior_employee_donations
    })

