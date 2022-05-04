from django import template


register = template.Library()


@register.filter
def range_(number):
	return range(number)


@register.simple_tag
def index_(lst, index):
	return lst[index] if index < len(lst) else False
