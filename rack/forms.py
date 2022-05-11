from django import forms
from django.core.exceptions import ValidationError

from .models import Rack, Server
from .utils import parser_length


class RackCreateForm(forms.ModelForm):
	class Meta:
		model = Rack
		fields = ['title', 'size']


class ServerCreateForm(forms.Form):
	title = forms.CharField(label='Метка')
	length = forms.CharField(label='Размер')
	s = forms.ChoiceField(choices=(('u', 'u'), ('1/3u', '1/3u')), label='Мера')
	note = forms.CharField(label='Заметки', widget=forms.Textarea, required=False)
	color = forms.CharField(widget=forms.TextInput(attrs={'type': 'color'}), initial='#c9c9c9')

	def clean(self):
		data = self.cleaned_data
		try:
			data['length'] = int(data['length']) if data['s'] == '1/3u' else int(
				data['length']) * 3
		except:
			data['length'] = parser_length(data['length'])
			if not data['length']:
				raise ValidationError('Не удалось расшифровать размер сервера')
		data.pop('s')
		return data


class ServerNoteForm(forms.ModelForm):

	class Meta:
		model = Server
		fields = ['note']
		widgets = {'note': forms.Textarea}
