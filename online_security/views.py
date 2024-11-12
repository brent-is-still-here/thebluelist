from django.shortcuts import render
from django.db.models import Q
from .models import Category, Recommendation, Solution

def security_landing(request):
    """Landing page for the security center"""
    return render(request, 'online_security/landing.html')

def security_browse(request):
    """Browse security recommendations with filtering"""
    # Get all filter parameters
    query = request.GET.get('q', '').strip()
    category_id = request.GET.get('category')
    difficulty = request.GET.get('difficulty')
    cost = request.GET.get('cost')

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

    if difficulty:
        recommendations = recommendations.filter(importance=difficulty)

    if cost:
        recommendations = recommendations.filter(solutions__cost_duration=cost)

    # Get all categories for the filter dropdown
    categories = Category.objects.all().order_by('order', 'name')

    context = {
        'recommendations': recommendations,
        'categories': categories,
        # Pass the current filters back to the template
        'current_filters': {
            'query': query,
            'category': category_id,
            'difficulty': difficulty,
            'cost': cost,
        }
    }

    return render(request, 'online_security/browse.html', context)
