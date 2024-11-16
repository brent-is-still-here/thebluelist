from django.http import JsonResponse
from django.views.decorators.http import require_GET
from companies.models import (
    ProductCategory, 
    ServiceCategory
)

@require_GET
def filter_categories(request):
    query = request.GET.get('q', '').strip().lower()
    category_type = request.GET.get('type')
    
    if category_type not in ['services', 'products']:
        return JsonResponse({'error': 'Invalid category type'}, status=400)
    
    CategoryModel = ServiceCategory if category_type == 'services' else ProductCategory
    
    if query:
        # First, find all categories that match the query
        matching_categories = CategoryModel.objects.filter(
            name__icontains=query
        )
        
        # Get IDs of matching categories
        matching_ids = set(matching_categories.values_list('id', flat=True))
        
        # For matching parents, get all their children
        child_ids = set(CategoryModel.objects.filter(
            parent__in=matching_categories
        ).values_list('id', flat=True))
        
        # For matching children, get their parents
        parent_ids = set(matching_categories.exclude(
            parent=None
        ).values_list('parent__id', flat=True))
        
        # Combine all IDs
        all_relevant_ids = matching_ids | child_ids | parent_ids
        
        # Get all categories in a single query
        categories = CategoryModel.objects.filter(
            id__in=all_relevant_ids
        ).select_related('parent').order_by('name')
    else:
        # If no query, return all categories
        categories = CategoryModel.objects.all().select_related('parent').order_by('name')
    
    results = []
    for cat in categories:
        category_data = {
            'id': cat.id,
            'name': cat.name,
            'parent_id': cat.parent.id if cat.parent else None,
            'parent_name': cat.parent.name if cat.parent else None
        }
        results.append(category_data)
    
    return JsonResponse({'results': results})
