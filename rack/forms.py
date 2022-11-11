from .models import Rack, Server, Port, FavoriteColor
from .services.widgets import ColorInput
from .services.port import PortConnectionParser, PortNotFoundError, PortHelper, PortIsNotFreeError
from .services.rack import RackHelper, NoFreePositionOnRackError
from .services.server import ServerLengthParser, ServerLengthParseError

from django import forms
from django.core.exceptions import ValidationError


class RackUpdateForm(forms.ModelForm):

	class Meta:
		model = Rack
		fields = ['title', 'note']
		widgets = {'note': forms.Textarea(attrs={'cols': 25})}


class RackCreateForm(forms.ModelForm):
	size = forms.IntegerField(label='Размер', min_value=1, initial=1)

	class Meta:
		model = Rack
		fields = ['title', 'size']

	def clean_size(self):
		size = self.cleaned_data.get('size')
		return size * 3


class ServerUpdateForm(forms.ModelForm):

	class Meta:
		model = Server
		fields = ['title', 'color', 'note', 'base_speed', 'base_material']
		widgets = {
			'color': ColorInput(favorite_colors=FavoriteColor.objects.all()),
			'note':  forms.Textarea(attrs={'rows': 5})
		}


class ServerCreateForm(forms.ModelForm):
	length = forms.CharField(label='Размер')
	unit = forms.ChoiceField(label='Мера', choices=(('u', 'u'), ('1/3u', '1/3u')))
	count_ports = forms.IntegerField(label='Портов', min_value=0, initial=1)
	color = forms.CharField(
		label='Цвет', widget=ColorInput(favorite_colors=FavoriteColor.objects.all()), initial='#c9c9c9'
	)

	class Meta:
		model = Server
		fields = ['title', 'length', 'unit', 'color', 'note', 'count_ports', 'base_speed', 'base_material', 'rack']
		widgets = {
			'note': forms.Textarea(attrs={'cols': 25}),
			'rack': forms.HiddenInput(),
		}

	def clean_length(self):
		parser = ServerLengthParser(self.cleaned_data.get('length'))
		try:
			return parser.parse_string(self.data.get('unit'))
		except ServerLengthParseError:
			raise ValidationError('Не удалось расшифровать размер сервера')


class ServerUpdatePositionForm(forms.ModelForm):
	position = forms.CharField(widget=forms.HiddenInput(attrs={'id': 'move_value'}))

	class Meta:
		model = Server
		fields = ['position']

	def clean_position(self):
		position = self.cleaned_data.get('position')
		rack = RackHelper(Rack.objects.get(pk=self.instance.rack_id))

		if position.isdigit():
			position_range = range(int(position), int(position) + 1)
		elif position == 'up1':
			position_range = range(self.instance.position - 1, -1, -1)
		elif position == 'up3':
			position_range = range(self.instance.position - 3, -1, -1)
		elif position == 'down1':
			position_range = range(self.instance.position + 1, rack.rack.size - self.instance.length + 1)
		elif position == 'down3':
			position_range = range(self.instance.position + 3, rack.rack.size - self.instance.length + 1)
		elif position == 'max':
			position_range = range(rack.rack.size - self.instance.length, self.instance.position, -1)
		elif position == 'min':
			position_range = range(self.instance.position)
		else:
			raise ValidationError('Недопустимый параметр в аргументе position')

		try:
			return rack.get_free_position(self.instance, position_range)
		except NoFreePositionOnRackError:
			raise ValidationError('Сервер не удалось переместить. Проверьте, что выбранная позиция свободна.')


class ServerNoteForm(forms.ModelForm):

	class Meta:
		model = Server
		fields = ['note']
		widgets = {'note': forms.Textarea(attrs={'rows': 5})}


class PortForm(forms.ModelForm):

	class Meta:
		model = Port
		fields = ['color', 'speed', 'material', 'note', 'connection']
		widgets = {
			'color': ColorInput(favorite_colors=FavoriteColor.objects.all()),
			'note': forms.Textarea(attrs={'rows': 3, }),
			'connection': forms.Textarea(attrs={'rows': 3, }),
		}


class PortUpdateForm(PortForm):

	class Meta(PortForm.Meta):
		pass

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.communication_port = None
		self.speed = None

	def clean_connection(self):
		connection = self.cleaned_data.get('connection')
		parser = PortConnectionParser(connection)
		parser_data = parser.parse()

		if parser_data.script:
			try:
				communication_port = PortHelper.search_port(parser_data.script)
				PortHelper.check_port_free(communication_port)
				self.communication_port = communication_port
				self.speed = parser_data.script.speed
			except (PortNotFoundError, PortIsNotFreeError) as error:
				raise ValidationError(error)

		return parser_data.string

	def save(self, commit=True):
		if self.communication_port:
			current_link = self.instance.link.first()

			if current_link:
				current_link.link.clear()

			self.instance.link.set([self.communication_port], through_defaults={'speed': self.speed})
			self.communication_port.link.set([self.instance], through_defaults={'speed': self.speed})
		return super().save(commit)


class PortCreateForm(PortForm):
	count = forms.IntegerField(label='Количество портов', min_value=1, initial=1)

	class Meta(PortForm.Meta):
		fields = ['color', 'speed', 'material', 'note', 'count', 'server']
		widgets = ({
			'server': forms.HiddenInput(),
			'color': ColorInput(favorite_colors=FavoriteColor.objects.all()),
			'note': forms.Textarea(attrs={'rows': 3, }),
			'connection': forms.Textarea(attrs={'rows': 3, }),
		})


class FavoriteColorAdminForm(forms.ModelForm):

	class Meta:
		model = FavoriteColor
		fields = '__all__'
		widgets = {
			'color': forms.TextInput(attrs={'type': 'color'})
		}
