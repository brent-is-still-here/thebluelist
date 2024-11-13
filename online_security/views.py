from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.db.models import Q
from .models import Category, Recommendation, Solution

def security_assessment(request):
    if request.method == 'POST':
        # Process form data
        results = {
            'needs_action': [],
            'completed': [],
            'not_applicable': []
        }
        
        # Get all recommendations that were answered in the form
        for key, value in request.POST.items():
            if key.startswith('recommendation_'):
                try:
                    recommendation_id = int(key.split('_')[1])
                    recommendation = Recommendation.objects.get(id=recommendation_id)
                    
                    if value == 'no':
                        results['needs_action'].append(recommendation.id)
                    elif value == 'yes':
                        results['completed'].append(recommendation.id)
                    elif value == 'na':
                        results['not_applicable'].append(recommendation.id)
                except Exception as e:
                    messages.error(request, f"Error processing responses: {str(e)}")
                    return redirect('security_assessment')

        try:
            # Store results in session
            request.session['assessment_results'] = {
                'needs_action': results['needs_action'],
                'completed': results['completed'],
                'not_applicable': results['not_applicable']
            }
            return redirect('security_assessment_results')
        except Exception as e:
            messages.error(request, f"Error saving results: {str(e)}")
            return redirect('security_assessment')
    
    # GET request - show the assessment form
    categories = Category.objects.prefetch_related('recommendations').all()
    return render(request, 'online_security/assessment.html', {
        'categories': categories,
        'total_categories': categories.count(),
    })

def security_assessment_results(request):
    # Get results from session
    session_results = request.session.get('assessment_results')
    if not session_results:
        messages.error(request, 'Please complete the security assessment first.')
        return redirect('security_assessment')
    
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        recommendation_id = request.POST.get('recommendation_id')
        if recommendation_id:
            # Move recommendation from needs_action to completed
            recommendation_id = int(recommendation_id)
            if recommendation_id in session_results['needs_action']:
                session_results['needs_action'].remove(recommendation_id)
                if 'completed' not in session_results:
                    session_results['completed'] = []
                session_results['completed'].append(recommendation_id)
                request.session['assessment_results'] = session_results
                
                return JsonResponse({
                    'status': 'success',
                    'needs_action_count': len(session_results['needs_action']),
                    'completed_count': len(session_results['completed'])
                })
        return JsonResponse({'status': 'error'}, status=400)
    
    # GET request - show results
    results = {
        'needs_action': Recommendation.objects.filter(
            id__in=session_results['needs_action']
        ).prefetch_related('categories', 'solutions'),
        'completed': Recommendation.objects.filter(
            id__in=session_results['completed']
        ),
        'not_applicable': Recommendation.objects.filter(
            id__in=session_results.get('not_applicable', [])
        )
    }
    
    return render(request, 'online_security/assessment_results.html', {
        'results': results
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
