from django.db.models import Case, IntegerField, Q, Value, When
from django.shortcuts import render
from companies.models import (
    Business
)

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
