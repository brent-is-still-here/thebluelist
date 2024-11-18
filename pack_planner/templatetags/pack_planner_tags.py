from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get an item from a dictionary using string key"""
    return dictionary.get(str(key))

@register.filter
def importance_class(importance):
    """Return appropriate CSS classes for importance level"""
    classes = {
        'critical': 'bg-red-100 text-red-800',
        'recommended': 'bg-blue-100 text-blue-800',
        'optional': 'bg-gray-100 text-gray-800'
    }
    return classes.get(importance.lower(), '')

@register.filter
def display_importance(importance):
    """Convert importance to display format"""
    return importance.title() if importance else ''