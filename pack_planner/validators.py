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
        # New fields are optional but must be boolean if present
        boolean_fields = {'go_bag', 'seventy_two_hr_bag'}
        for field in boolean_fields:
            if field in category and not isinstance(category[field], bool):
                raise ValidationError(f"Category {field} must be a boolean value")

    # Validate items
    for item in data.get('items', []):
        if not all(key in item for key in {'name', 'description', 'category', 'importance'}):
            raise ValidationError("Invalid item structure")
        # New fields are optional but must be boolean if present
        boolean_fields = {
            'go_bag', 'seventy_two_hr_bag', 'conditional_applicability',
            'for_adults', 'for_children', 'for_pets', 'for_cats', 'for_dogs',
            'for_small_animals', 'for_disabled', 'for_elderly', 'for_on_foot',
            'for_bicycle', 'for_vehicle', 'for_public_transit'
        }
        for field in boolean_fields:
            if field in item and not isinstance(item[field], bool):
                raise ValidationError(f"Item {field} must be a boolean value")

    # Validate products
    for product in data.get('products', []):
        if not all(key in product for key in {'name', 'description', 'item'}):
            raise ValidationError("Invalid product structure")
        # New fields are optional but must be boolean if present
        boolean_fields = {'go_bag', 'seventy_two_hr_bag', 'is_available'}
        for field in boolean_fields:
            if field in product and not isinstance(product[field], bool):
                raise ValidationError(f"Product {field} must be a boolean value")