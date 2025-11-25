from django import template
from django.db.models import Sum

register = template.Library()

@register.simple_tag
def total_category_posts():
    from ..models import Category
    total = Category.objects.aggregate(total=Sum('num_posts'))['total']
    return total or 0