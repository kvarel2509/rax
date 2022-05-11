from django import template
from ..forms import ServerNoteForm


register = template.Library()


@register.filter
def range_(number):
	return range(number)


@register.simple_tag
def index_(lst, index):
	return lst[index] if index < len(lst) else False


@register.inclusion_tag('rack/note.html')
def get_note_form(obj):
	return {'object': obj, 'form_note': ServerNoteForm(instance=obj)}
