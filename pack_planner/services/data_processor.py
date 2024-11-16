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
                        'order': item_data.get('order', 0)
                    }
                )
                if created:
                    self.stats['items'] += 1
                    
                # Handle alternatives
                if 'alternatives' in item_data:
                    alt_items = Item.objects.filter(name__in=item_data['alternatives'])
                    item.alternatives.set(alt_items)
                    
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
            