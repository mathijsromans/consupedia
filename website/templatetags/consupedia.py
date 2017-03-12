from django import template

from product.models import Rating

register = template.Library()


@register.assignment_tag
def get_product_rating(product, user):
	ratings = product.get_rating(user)
	if ratings.exists():
		return ratings[0].rating
	return None
