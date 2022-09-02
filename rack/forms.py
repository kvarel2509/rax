from .models import Rack, Server, Port
from .services.port import PortConnectionParser, PortNotFoundError, PortHelper, PortIsNotFreeError
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


class ServerUpdateForm(forms.ModelForm):

	class Meta:
		model = Server
		fields = ['title', 'color', 'note', 'base_speed', 'base_material']
		widgets = {
			'color': forms.TextInput(attrs={'type': 'color'}),
			'note':  forms.Textarea(attrs={'rows': 5})
		}


class ServerCreateForm(forms.ModelForm):
	length = forms.CharField(label='Размер')
	unit = forms.ChoiceField(label='Мера', choices=(('u', 'u'), ('1/3u', '1/3u')))
	count_ports = forms.IntegerField(label='Портов', min_value=0, initial=1)
	color = forms.CharField(label='Цвет', widget=forms.TextInput(attrs={'type': 'color'}), initial='#c9c9c9')

	class Meta:
		model = Server
		fields = ['title', 'length', 'unit', 'color', 'note', 'count_ports', 'base_speed', 'base_material']
		widgets = {'note': forms.Textarea(attrs={'cols': 25})}

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._length = None

	def clean(self):
		super().clean()
		parser = ServerLengthParser(self.cleaned_data.get('length'))
		try:
			self._length = parser.parse_string(self.cleaned_data.get('unit'))
			self.cleaned_data['length'] = self._length
		except ServerLengthParseError:
			raise ValidationError('Не удалось расшифровать размер сервера')
		return self.cleaned_data


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
			'color': forms.TextInput(attrs={'type': 'color', }),
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
		fields = ['color', 'speed', 'material', 'note', 'count']
