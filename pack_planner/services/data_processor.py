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
    Returns a dictionary of packs, each containing categories and their items.
    """
    packs = {}
    
    # Get base query for all items with their categories
    base_items = Item.objects.select_related('category').all()
    
    # Apply transportation mode filter
    transport_type = assessment_data.get('transportType', 'walking')
    if transport_type == 'walking':
        base_items = base_items.filter(for_on_foot=True)
    elif transport_type == 'bicycle':
        base_items = base_items.filter(for_bicycle=True)
    elif transport_type == 'car':
        base_items = base_items.filter(for_vehicle=True)
    elif transport_type == 'public':
        base_items = base_items.filter(for_public_transit=True)

    # Generate adult packs
    num_adults = assessment_data.get('adults', 1)
    for i in range(num_adults):
        pack_name = f"Adult pack {i + 1}"
        adult_items = base_items.filter(for_adults=True)
        
        if assessment_data.get('hasElderly'):
            adult_items = adult_items | base_items.filter(for_elderly=True)
        if assessment_data.get('hasDisabled'):
            adult_items = adult_items | base_items.filter(for_disabled=True)
            
        # Organize items by category
        categories_dict = {}
        for item in adult_items:
            if item.category not in categories_dict:
                categories_dict[item.category] = []
            categories_dict[item.category].append(item)
            
        # Sort categories by order
        sorted_categories = sorted(categories_dict.items(), key=lambda x: (x[0].order, x[0].name))
        packs[pack_name] = sorted_categories

    # Generate child packs
    num_children = assessment_data.get('children', 0)
    for i in range(num_children):
        pack_name = f"Child pack {i + 1}"
        child_items = base_items.filter(for_children=True)
        
        if assessment_data.get('hasDisabled'):
            child_items = child_items | base_items.filter(for_disabled=True, for_children=True)
            
        # Organize items by category
        categories_dict = {}
        for item in child_items:
            if item.category not in categories_dict:
                categories_dict[item.category] = []
            categories_dict[item.category].append(item)
            
        # Sort categories by order
        sorted_categories = sorted(categories_dict.items(), key=lambda x: (x[0].order, x[0].name))
        packs[pack_name] = sorted_categories

    # Generate pet packs
    if assessment_data.get('hasPets'):
        for pet_type in assessment_data.get('petTypes', []):
            pack_name = f"{pet_type.title()} pack 1"
            pet_items = base_items.filter(for_pets=True)
            
            # Organize items by category
            categories_dict = {}
            for item in pet_items:
                if item.category not in categories_dict:
                    categories_dict[item.category] = []
                categories_dict[item.category].append(item)
                
            # Sort categories by order
            sorted_categories = sorted(categories_dict.items(), key=lambda x: (x[0].order, x[0].name))
            packs[pack_name] = sorted_categories

    return packs