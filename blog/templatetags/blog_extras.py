# blog/templatetags/blog_extras.py
from django import template

register = template.Library()

@register.filter
def intcomma(value):
    """
    Converts an integer to a string with comma separators.
    Example: 1000000 -> "1,000,000"
    """
    try:
        value = int(value)
        return "{:,}".format(value)
    except (ValueError, TypeError):
        return value

@register.filter
def compact_number(value):
    """
    Converts large numbers to compact format.
    Example: 1000000 -> "1M", 50000 -> "50K"
    """
    try:
        value = int(value)
        if value >= 1000000:
            return f"{value/1000000:.1f}M".rstrip('0').rstrip('.')
        elif value >= 1000:
            return f"{value/1000:.1f}K".rstrip('0').rstrip('.')
        return str(value)
    except (ValueError, TypeError):
        return value