import json
from django.core.exceptions import ValidationError

def validate_file_extension(value):
    if not value.name.endswith('.json'):
        raise ValidationError('Only JSON files are allowed')

def validate_json_structure(data):
    """Validate the structure of the JSON data"""
    required_keys = {'categories', 'items', 'products'}
    if not all(key in data for key in required_keys):
        raise ValidationError(f"JSON must contain these top-level keys: {required_keys}")
    
    # Validate categories
    for category in data.get('categories', []):
        if not all(key in category for key in {'name', 'description', 'importance'}):
            raise ValidationError("Invalid category structure")

    # Validate items
    for item in data.get('items', []):
        if not all(key in item for key in {'name', 'description', 'category', 'importance'}):
            raise ValidationError("Invalid item structure")

    # Validate products
    for product in data.get('products', []):
        if not all(key in product for key in {'name', 'description', 'item'}):
            raise ValidationError("Invalid product structure")
