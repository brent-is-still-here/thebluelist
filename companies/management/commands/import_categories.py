import csv
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from companies.models import ProductCategory, ServiceCategory
from django.db import transaction

class Command(BaseCommand):
    help = 'Import product and service categories from CSV files'

    def add_arguments(self, parser):
        parser.add_argument('products_csv', type=str, help='Path to products CSV file')
        parser.add_argument('services_csv', type=str, help='Path to services CSV file')

    def handle(self, *args, **options):
        products_file = options['products_csv']
        services_file = options['services_csv']

        # Import product categories
        with transaction.atomic():
            self.stdout.write('Importing product categories...')
            with open(products_file, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    name = row['name'].strip()
                    parent = row.get('parent', '').strip()
                    
                    product_category, created = ProductCategory.objects.get_or_create(
                        name=name,
                        defaults={
                            'parent': parent,
                            'slug': slugify(name)
                        }
                    )
                    
                    if created:
                        self.stdout.write(self.style.SUCCESS(f'Created product category: {name}'))
                    else:
                        self.stdout.write(self.style.WARNING(f'Product category already exists: {name}'))

        # Import service categories
        with transaction.atomic():
            self.stdout.write('Importing service categories...')
            with open(services_file, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    name = row['name'].strip()
                    parent = row.get('parent', '').strip()
                    
                    service_category, created = ServiceCategory.objects.get_or_create(
                        name=name,
                        defaults={
                            'parent': parent,
                            'slug': slugify(name)
                        }
                    )
                    
                    if created:
                        self.stdout.write(self.style.SUCCESS(f'Created service category: {name}'))
                    else:
                        self.stdout.write(self.style.WARNING(f'Service category already exists: {name}'))

        self.stdout.write(self.style.SUCCESS('Import completed successfully!'))

    def _clean_data(self, value):
        """Clean input data by stripping whitespace and handling empty values"""
        if value is None:
            return ''
        return str(value).strip()