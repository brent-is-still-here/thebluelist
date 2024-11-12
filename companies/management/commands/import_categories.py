
import json
import os
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.conf import settings
from companies.models import ProductCategory, ServiceCategory
from django.db import transaction

class Command(BaseCommand):
    help = 'Import product and service categories from JSON files'

    def handle(self, *args, **options):
        products_file = os.path.join(settings.BASE_DIR, 'data', 'product_categories.json')
        services_file = os.path.join(settings.BASE_DIR, 'data', 'service_categories.json')

        # Verify files exist
        if not os.path.exists(products_file):
            self.stdout.write(self.style.ERROR(f'Products JSON file not found at: {products_file}'))
            return
        if not os.path.exists(services_file):
            self.stdout.write(self.style.ERROR(f'Services JSON file not found at: {services_file}'))
            return

        try:
            # Import product categories
            with transaction.atomic():
                self.stdout.write('Importing product categories...')
                with open(products_file, 'r', encoding='utf-8') as file:
                    products_data = json.load(file)
                    self._import_categories(products_data['categories'], ProductCategory)

            # Import service categories
            with transaction.atomic():
                self.stdout.write('Importing service categories...')
                with open(services_file, 'r', encoding='utf-8') as file:
                    services_data = json.load(file)
                    self._import_categories(services_data['categories'], ServiceCategory)

            self.stdout.write(self.style.SUCCESS('Import completed successfully!'))

        except json.JSONDecodeError as e:
            self.stdout.write(self.style.ERROR(f'Error parsing JSON file: {str(e)}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error during import: {str(e)}'))
            raise

    def _import_categories(self, categories, CategoryModel, parent=None):
        """
        Recursively import categories and their children
        
        Args:
            categories (list): List of category dictionaries from JSON
            CategoryModel: Either ProductCategory or ServiceCategory model class
            parent: Parent category instance (None for top-level categories)
        """
        for category_data in categories:
            name = category_data.get('name', '').strip()
            
            if not name:
                self.stdout.write(self.style.WARNING(f"Skipping category with missing name"))
                continue

            try:
                # Create or update the category
                category, created = CategoryModel.objects.get_or_create(
                    name=name,
                    defaults={
                        'slug': slugify(name),
                        'parent': parent
                    }
                )

                # If category exists but parent is different, update it
                if not created and category.parent != parent:
                    category.parent = parent
                    category.save()

                action = 'Created' if created else 'Updated'
                self.stdout.write(
                    self.style.SUCCESS(f'{action} category: {name}') if created 
                    else self.style.WARNING(f'{action} category: {name}')
                )

                # Process children recursively
                children = category_data.get('children', [])
                if children:
                    self._import_categories(children, CategoryModel, parent=category)

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error processing category {name}: {str(e)}')
                )
                continue