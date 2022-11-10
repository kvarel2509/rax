from django.forms.widgets import Input


class ColorInput(Input):
	input_type = 'color'
	template_name = 'rack/color_widget.html'

	def __init__(self, attrs=None, favorite_colors=None):
		super().__init__(attrs)
		self.favorite_colors = favorite_colors if favorite_colors else ()

	def get_context(self, *args, **kwargs):
		ctx = super().get_context(*args, **kwargs)
		ctx['favorite_colors'] = self.favorite_colors
		return ctx
