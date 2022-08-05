from .forms import (
	ServerNoteForm,
	ServerCreateForm,
	RackCreateForm,
	PortUpdateForm,
	PortCreateForm,
	ServerUpdateForm,
	RackUpdateForm,
)
from .models import Rack, Server, Port
from .services.rack import RackHelper
from .services.server import ServerHelper

from django.urls import reverse_lazy
from django.views import generic
from django.contrib import messages
from django.http import HttpResponseRedirect


class RackCreateView(generic.CreateView):
	"""Для создания новой полки"""
	template_name = 'rack/rack_create.html'
	form_class = RackCreateForm

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.object = None

	def form_valid(self, form):
		self.object = form.save(commit=False)
		self.object.size *= 3
		self.object.space = [self.object.size]
		self.object.save()
		return HttpResponseRedirect(self.get_success_url())


class RackListView(generic.ListView):
	"""Представление для отображения списка полок"""
	model = Rack


class RackDetailView(generic.DetailView):
	"""Для показа полки"""
	model = Rack

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		rack = RackHelper(self.object)
		context['rack'] = rack.get_context_for_detail_view()
		context['numbering'] = []

		for i in range(self.object.size // 3, 0, -1):
			context['numbering'].extend([
				{'length': 3, 'value': i},
				{'length': 0, 'value': None},
				{'length': 0, 'value': None}
			])

		context['server_creation_form'] = ServerCreateForm()
		context['rack_update_form'] = RackUpdateForm(instance=self.object)
		return context


class RackUpdateView(generic.UpdateView):
	model = Rack
	form_class = RackUpdateForm

	def get_success_url(self):
		return reverse_lazy('rack_detail', kwargs={'pk': self.object.pk})


class RackDeleteView(generic.DeleteView):
	model = Rack
	success_url = reverse_lazy('rack_list')


class ServerDetailView(generic.DetailView):
	model = Server

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['ports'] = [{'port': port, 'form': PortUpdateForm(instance=port)} for port in self.object.port_set.all()]
		context['numerator_ports'] = range(1, len(context['ports']) + 1)
		context['create_port_form'] = PortCreateForm(
			initial={'speed': self.object.base_speed, 'material': self.object.base_material}
		)
		return context


class ServerUpdateView(generic.UpdateView):
	model = Server
	form_class = ServerUpdateForm


class PortUpdateView(generic.UpdateView):
	model = Port
	form_class = PortUpdateForm

	def get_success_url(self):
		return reverse_lazy('server_detail', kwargs={'pk': self.object.server_id})


class PortCreateView(generic.CreateView):
	model = Port
	form_class = PortCreateForm

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.server = None

	def form_valid(self, form):
		self.server = Server.objects.get(pk=self.kwargs.get('pk'))
		port = form.save(commit=False)
		port.server = self.server
		Port.objects.bulk_create([port for _ in range(form.cleaned_data['count'])])
		messages.success(self.request, 'Порты успешно добавлены')
		return HttpResponseRedirect(self.get_url())

	def get_url(self):
		return reverse_lazy('server_detail', kwargs={'pk': self.server.pk})


class PortDeleteView(generic.View):
	def post(self, *args, **kwargs):
		server = ServerHelper(Server.objects.get(pk=kwargs.get('pk')))
		server.delete_ports(self.request.POST.getlist('del-port'))
		return HttpResponseRedirect(self.get_url())

	def get_url(self):
		return reverse_lazy('server_detail', kwargs={'pk': self.kwargs.get('pk')})


class ServerCreateView(generic.FormView):
	"""Для создания сервера"""
	template_name = 'rack/server_create.html'
	model = Server
	form_class = ServerCreateForm

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.rask_pk = None

	def post(self, *args, **kwargs):
		self.rask_pk = self.kwargs.get('pk')
		return super().post(*args, **kwargs)

	def form_valid(self, form):
		rack = RackHelper(Rack.objects.get(pk=self.rask_pk))

		if rack.check_free_space(form.cleaned_data.get('length')):
			form.cleaned_data['rack'] = rack.rack
			server = ServerHelper().create_server(form.cleaned_data)
			server = ServerHelper(server)
			rack.put_server_in_space(server)
			messages.success(self.request, 'Сервер успешно добавлен')
		else:
			messages.error(self.request, 'Сервер не добавлен. Нет свободного места')

		return HttpResponseRedirect(self.get_url())

	def form_invalid(self, form):
		messages.error(self.request, form.non_field_errors())
		return HttpResponseRedirect(self.get_url())

	def get_url(self):
		return reverse_lazy('rack_detail', kwargs={'pk': self.rask_pk})


class ServerNoteCreateView(generic.UpdateView):
	"""Для создания заметки на сервер"""
	form_class = ServerNoteForm
	template_name = 'rack/server_note_create.html'
	model = Server

	def get_success_url(self):
		return reverse_lazy('rack_detail', kwargs={'pk': self.object.rack_id})


class MoveServerView(generic.View):
	"""Для перемещения сервера по полке"""

	def post(self, request, *args, **kwargs):
		server_pk = self.kwargs.get('pk')
		server = ServerHelper(Server.objects.get(pk=server_pk))
		rack = RackHelper(server.server.rack)
		rack.move_server_in_space(server, self.request.POST.get('move_type'))
		return HttpResponseRedirect(self.get_url(rack.rack.pk))

	@staticmethod
	def get_url(rack_pk):
		return reverse_lazy('rack_detail', kwargs={'pk': rack_pk})


class ServerDeleteView(generic.DeleteView):
	model = Server

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.object = None

	def delete(self, request, *args, **kwargs):
		self.object = self.get_object()
		server = ServerHelper(self.object)
		rack = RackHelper(self.object.rack)
		rack.delete_server_from_space(server)
		self.object.delete()
		return HttpResponseRedirect(self.get_url(rack))

	@staticmethod
	def get_url(rack):
		return reverse_lazy('rack_detail', kwargs={'pk': rack.rack.pk})
