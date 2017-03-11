from django import template

from product.models import Rating

register = template.Library()


@register.assignment_tag
def get_product_rating(product, user):
    ratings = Rating.objects.filter(product=product, user=user)
    if ratings:
        return ratings[0].rating
    return None