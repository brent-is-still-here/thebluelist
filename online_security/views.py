from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Category, Recommendation, Solution

def security_assessment(request):
    if request.method == 'POST':
        # Handle form submission and generate recommendations
        # We'll implement this next
        pass
    
    categories = Category.objects.prefetch_related('recommendations').all()
    
    return render(request, 'online_security/assessment.html', {
        'categories': categories,
        'total_categories': categories.count(),
    })

def security_browse(request):
    """Browse security recommendations with filtering"""
    # Get all filter parameters
    query = request.GET.get('q', '').strip()
    category_id = request.GET.get('category')
    severity = request.GET.get('severity')

    # Start with all recommendations
    recommendations = Recommendation.objects.all()

    # Apply filters
    if query:
        recommendations = recommendations.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(solutions__name__icontains=query)
        ).distinct()

    if category_id:
        recommendations = recommendations.filter(categories__id=category_id)

    if severity:
        recommendations = recommendations.filter(importance=severity)

    # Get all categories for the filter dropdown
    categories = Category.objects.all().order_by('order', 'name')

    context = {
        'recommendations': recommendations,
        'categories': categories,
        # Pass the current filters back to the template
        'current_filters': {
            'query': query,
            'category': category_id,
            'severity': severity,
        }
    }

    return render(request, 'online_security/browse.html', context)

def security_landing(request):
    """Landing page for the security center"""
    return render(request, 'online_security/landing.html')

def security_recommendation_detail(request, pk):
    recommendation = get_object_or_404(
        Recommendation.objects.prefetch_related(
            'categories',
            'solutions'
        ),
        pk=pk
    )
    
    return render(request, 'online_security/recommendation_detail.html', {
        'recommendation': recommendation
    })
