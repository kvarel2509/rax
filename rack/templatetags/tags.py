from django import template


register = template.Library()


@register.filter
def get_range(number):
	return range(number)


@register.simple_tag
def get_item(lst, index):
	return lst[index] if index < len(lst) else False
