from django.forms.widgets import Input


class ColorInput(Input):
	"""
	allows you to display additional colors in the widget. To do this, pass the favorite_colors argument,
	which is a lambda function that returns a list of elements with the keys title, color.

	"""
	input_type = 'color'
	template_name = 'rack/color_widget.html'

	def __init__(self, attrs=None, favorite_colors=None):
		super().__init__(attrs)
		self.favorite_colors = lambda: () if favorite_colors is None else favorite_colors

	def get_context(self, *args, **kwargs):
		ctx = super().get_context(*args, **kwargs)
		ctx['widget']['favorite_colors'] = self.favorite_colors()
		return ctx
