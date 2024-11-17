from collections import defaultdict
from django.db import transaction
from pack_planner.models import Category, Item, Product

class DataProcessor:
    def __init__(self, upload_type):
        self.upload_type = upload_type
        self.stats = {'categories': 0, 'items': 0, 'products': 0}

    def process_data(self, data):
        if self.upload_type == 'full':
            self._clear_existing_data()
            
        self._process_categories(data.get('categories', []))
        self._process_items(data.get('items', []))
        self._process_products(data.get('products', []))
        
        return self.stats

    def _clear_existing_data(self):
        with transaction.atomic():
            Product.objects.all().delete()
            Item.objects.all().delete()
            Category.objects.all().delete()

    def _process_categories(self, categories):
        for cat_data in categories:
            category, created = Category.objects.update_or_create(
                name=cat_data['name'],
                defaults={
                    'description': cat_data['description'],
                    'importance': cat_data['importance'],
                    'order': cat_data.get('order', 0)
                }
            )
            if created:
                self.stats['categories'] += 1

    def _process_items(self, items):
        for item_data in items:
            try:
                category = Category.objects.get(name=item_data['category'])
                item, created = Item.objects.update_or_create(
                    name=item_data['name'],
                    defaults={
                        'description': item_data['description'],
                        'uses': item_data.get('uses', ''),
                        'category': category,
                        'importance': item_data['importance'],
                        'weight_note': item_data.get('weight_note', ''),
                        'special_considerations': item_data.get('special_considerations', ''),
                        'order': item_data.get('order', 0),
                        'for_adults': item_data.get('for_adults', True),
                        'for_children': item_data.get('for_children', False),
                        'for_pets': item_data.get('for_pets', False),
                        'for_disabled': item_data.get('for_disabled', False),
                        'for_elderly': item_data.get('for_elderly', False),
                        'for_on_foot': item_data.get('for_on_foot', True),
                        'for_bicycle': item_data.get('for_bicycle', True),
                        'for_vehicle': item_data.get('for_vehicle', True),
                        'for_public_transit': item_data.get('for_public_transit', True),
                    }
                )
                
                # Handle alternatives
                if 'alternatives' in item_data:
                    alt_items = Item.objects.filter(name__in=item_data['alternatives'])
                    item.alternatives.set(alt_items)
                
                if created:
                    self.stats['items'] += 1
            
            except Category.DoesNotExist:
                raise ValueError(f"Category not found: {item_data['category']}")

    def _process_products(self, products):
        for prod_data in products:
            try:
                item = Item.objects.get(name=prod_data['item'])
                product, created = Product.objects.update_or_create(
                    name=prod_data['name'],
                    item=item,
                    defaults={
                        'description': prod_data['description'],
                        'url': prod_data.get('url', ''),
                        'notes': prod_data.get('notes', ''),
                        'is_available': prod_data.get('is_available', True)
                    }
                )
                if created:
                    self.stats['products'] += 1
            
            except Item.DoesNotExist:
                raise ValueError(f"Item not found: {prod_data['item']}")
            
def generate_packs(assessment_data):
    """
    Generate packs based on the user's assessment data.
    Returns a structured dictionary of recommendations organized by importance.
    """
    recommendations = {
        'critical': [],
        'recommended': [],
        'optional': []
    }
    
    # Base query for all items
    items = Item.objects.select_related('category').all()
    
    # Apply transportation mode filter
    transport_type = assessment_data.get('transportType', 'walking')
    if transport_type == 'walking':
        items = items.filter(for_on_foot=True)
    elif transport_type == 'bicycle':
        items = items.filter(for_bicycle=True)
    elif transport_type == 'car':
        items = items.filter(for_vehicle=True)
    elif transport_type == 'public':
        items = items.filter(for_public_transit=True)
    
    # Create base set of items for number of adults
    num_adults = assessment_data.get('adults', 1)
    if num_adults > 0:
        adult_items = items.filter(for_adults=True)
        recommendations['critical'].extend(list(adult_items.filter(importance='critical')))
        recommendations['recommended'].extend(list(adult_items.filter(importance='recommended')))
        recommendations['optional'].extend(list(adult_items.filter(importance='optional')))
    
    # Add items for children if present
    num_children = assessment_data.get('children', 0)
    if num_children > 0:
        child_items = items.filter(for_children=True)
        recommendations['critical'].extend(list(child_items.filter(importance='critical')))
        recommendations['recommended'].extend(list(child_items.filter(importance='recommended')))
        recommendations['optional'].extend(list(child_items.filter(importance='optional')))
    
    # Add items for elderly if present
    if assessment_data.get('hasElderly'):
        elderly_items = items.filter(for_elderly=True)
        recommendations['critical'].extend(list(elderly_items.filter(importance='critical')))
        recommendations['recommended'].extend(list(elderly_items.filter(importance='recommended')))
        recommendations['optional'].extend(list(elderly_items.filter(importance='optional')))
    
    # Add items for disabled if present
    if assessment_data.get('hasDisabled'):
        disabled_items = items.filter(for_disabled=True)
        recommendations['critical'].extend(list(disabled_items.filter(importance='critical')))
        recommendations['recommended'].extend(list(disabled_items.filter(importance='recommended')))
        recommendations['optional'].extend(list(disabled_items.filter(importance='optional')))
    
    # Add items for pets if present
    if assessment_data.get('hasPets'):
        pet_items = items.filter(for_pets=True)
        recommendations['critical'].extend(list(pet_items.filter(importance='critical')))
        recommendations['recommended'].extend(list(pet_items.filter(importance='recommended')))
        recommendations['optional'].extend(list(pet_items.filter(importance='optional')))
    
    # Remove duplicates while preserving order
    for importance in recommendations:
        recommendations[importance] = list(dict.fromkeys(recommendations[importance]))
    
    return recommendations