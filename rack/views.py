from .forms import (
	ServerNoteForm,
	ServerCreateForm,
	RackCreateForm,
	PortUpdateForm,
	PortCreateForm,
	ServerUpdateForm,
	RackUpdateForm,
)
from .models import Rack, Server, Port, LinkPort
from .services.port import PortHelper
from .services.rack import RackHelper
from .services.server import ServerHelper

from django.urls import reverse_lazy
from django.views import generic
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin


class RackCreateView(LoginRequiredMixin, generic.CreateView):
	"""Для создания новой стойки"""
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


class RackListView(LoginRequiredMixin, generic.ListView):
	"""Представление для отображения списка стоек"""
	queryset = Rack.objects.filter(backside__isnull=True)


class RackDetailView(LoginRequiredMixin, generic.DetailView):
	"""Для показа стойки"""
	model = Rack

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		rack = RackHelper(self.object)
		context['space_main'] = rack.get_space_for_detail_view()
		rack_reverse_side = rack.get_reverse_side()
		context['reverse_side'] = rack_reverse_side

		if rack_reverse_side:
			context['space_reverse'] = RackHelper(rack_reverse_side).get_space_for_detail_view()
		else:
			context['space_reverse'] = [RackHelper.get_space_empty_row()] * rack.rack.size
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


class RackUpdateView(LoginRequiredMixin, generic.UpdateView):
	model = Rack
	form_class = RackUpdateForm

	def get_success_url(self):
		return reverse_lazy('rack_detail', kwargs={'pk': self.object.pk})


class RackDeleteView(LoginRequiredMixin, generic.DeleteView):
	model = Rack

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.object = None

	def delete(self, request, *args, **kwargs):
		self.object = self.get_object()
		success_url = self.get_success_url()

		if not self.object.backside:
			reverse_side = self.object.reverse_side.first()

			if reverse_side:
				reverse_side.delete()

		self.object.delete()
		return HttpResponseRedirect(success_url)

	def get_success_url(self):
		if not self.object.backside:
			return reverse_lazy('rack_list')
		else:
			return reverse_lazy('rack_detail', kwargs={'pk': self.object.reverse_side.first().pk})


class RackCreateBackSideView(LoginRequiredMixin, generic.View):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.rack_backside = None

	def get(self, request, *args, **kwargs):
		rack = RackHelper(Rack.objects.get(pk=self.kwargs.get('pk')))
		self.rack_backside = rack.create_rack_backside()
		return HttpResponseRedirect(self.get_url())

	def get_url(self):
		return reverse_lazy('rack_detail', kwargs={'pk': self.rack_backside.pk})


class ServerDetailView(LoginRequiredMixin, generic.DetailView):
	model = Server

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['ports'] = [{
			'port': port,
			'form': PortUpdateForm(instance=port),
			'link': port.link.first(),
			'through': LinkPort.objects.filter(port1=port).first()
		} for port in self.object.port_set.all().order_by('pk')]
		context['create_port_form'] = PortCreateForm(
			initial={'speed': self.object.base_speed, 'material': self.object.base_material}
		)
		return context


class ServerUpdateView(LoginRequiredMixin, generic.UpdateView):
	model = Server
	form_class = ServerUpdateForm


class PortUpdateView(LoginRequiredMixin, generic.UpdateView):
	model = Port
	form_class = PortUpdateForm

	def form_invalid(self, form):
		messages.error(self.request, 'Изменения не внесены. Проверьте правильность ввода')
		return HttpResponseRedirect(self.get_success_url())

	def get_success_url(self):
		return reverse_lazy('server_detail', kwargs={'pk': self.object.server_id})


class PortCreateView(LoginRequiredMixin, generic.CreateView):
	model = Port
	form_class = PortCreateForm

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.server = None

	def form_valid(self, form):
		self.server = Server.objects.get(pk=self.kwargs.get('pk'))
		current_ports_count = self.server.port_set.count()
		ports = [Port(
			color=form.cleaned_data.get('color'),
			speed=form.cleaned_data.get('speed'),
			material=form.cleaned_data.get('material'),
			server=self.server
		) for _ in range(form.cleaned_data['count'])]
		ports = PortHelper.ports_numbering(ports, current_ports_count + 1)
		Port.objects.bulk_create(ports, batch_size=50)
		return HttpResponseRedirect(self.get_url())

	def get_url(self):
		return reverse_lazy('server_detail', kwargs={'pk': self.server.pk})


class PortDeleteView(LoginRequiredMixin, generic.View):
	def post(self, *args, **kwargs):
		server = ServerHelper(Server.objects.get(pk=kwargs.get('pk')))
		server.delete_ports(self.request.POST.getlist('del-port'))
		return HttpResponseRedirect(self.get_url())

	def get_url(self):
		return reverse_lazy('server_detail', kwargs={'pk': self.kwargs.get('pk')})


class ServerCreateView(LoginRequiredMixin, generic.FormView):
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
		else:
			messages.error(self.request, 'Сервер не добавлен. Нет свободного места')

		return HttpResponseRedirect(self.get_url())

	def form_invalid(self, form):
		messages.error(self.request, form.non_field_errors())
		return HttpResponseRedirect(self.get_url())

	def get_url(self):
		return reverse_lazy('rack_detail', kwargs={'pk': self.rask_pk})


class ServerNoteCreateView(LoginRequiredMixin, generic.UpdateView):
	"""Для создания заметки на сервер"""
	form_class = ServerNoteForm
	template_name = 'rack/server_note_create.html'
	model = Server

	def get_success_url(self):
		return reverse_lazy('rack_detail', kwargs={'pk': self.object.rack_id})


class MoveServerView(LoginRequiredMixin, generic.View):
	"""Для перемещения сервера по стойке"""

	def post(self, request, *args, **kwargs):
		server_pk = self.kwargs.get('pk')
		server = ServerHelper(Server.objects.get(pk=server_pk))
		rack = RackHelper(server.server.rack)
		rack.move_server_in_space(server, self.request.POST.get('move_type'))
		print(rack.rack.space)
		return HttpResponseRedirect(self.get_url(rack.rack.pk))

	@staticmethod
	def get_url(rack_pk):
		return reverse_lazy('rack_detail', kwargs={'pk': rack_pk})


class ServerDeleteView(LoginRequiredMixin, generic.DeleteView):
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


class LinkPortDeleteView(LoginRequiredMixin, generic.DeleteView):
	model = LinkPort

	def delete(self, request, *args, **kwargs):
		LinkPort.objects.filter(port1_id__in=[self.kwargs.get('pk1'), self.kwargs.get('pk2')]).delete()
		return HttpResponseRedirect(self.get_success_url())

	def get_success_url(self):
		return reverse_lazy('server_detail', kwargs={'pk': self.kwargs.get('pk')})
