from .forms import (
	ServerNoteForm,
	ServerCreateForm,
	RackCreateForm,
	PortUpdateForm,
	PortCreateForm,
	ServerUpdateForm,
	RackUpdateForm,
	ServerUpdatePositionForm,
)
from .models import Rack, Server, Port, LinkPort
from .services.port import PortHelper
from .services.rack import RackHelper, NoFreePositionOnRackError
from .services.server import ServerHelper

from django.urls import reverse_lazy
from django.views import generic
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin


class RackCreateView(LoginRequiredMixin, generic.CreateView):
	model = Rack
	form_class = RackCreateForm


class RackListView(LoginRequiredMixin, generic.ListView):
	queryset = Rack.objects.filter(backside__isnull=True)


class RackDetailView(LoginRequiredMixin, generic.DetailView):
	model = Rack

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['server_list'] = [{
			'object': server,
			'note_form': ServerNoteForm(instance=server),
			'position_form': ServerUpdatePositionForm(instance=server)
		} for server in self.object.server_set.all()]
		context['reverse_side'] = self.object.reverse_side.first()
		context['server_creation_form'] = ServerCreateForm(initial={'rack': self.object.pk})
		context['rack_update_form'] = RackUpdateForm(instance=self.object)
		context['size_match'] = 15
		context['scale'] = [i for i in range(self.object.size // 3, 0, -1)]
		context['server_list_reverse_side'] = None

		if context['reverse_side']:
			context['server_list_reverse_side'] = context['reverse_side'].server_set.all()

		return context


class RackUpdateView(LoginRequiredMixin, generic.UpdateView):
	model = Rack
	form_class = RackUpdateForm


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
			initial={
				'speed': self.object.base_speed,
				'material': self.object.base_material,
				'server': self.object.pk,
			}
		)
		return context


class ServerUpdateView(LoginRequiredMixin, generic.UpdateView):
	model = Server
	form_class = ServerUpdateForm


class ServerCreateView(LoginRequiredMixin, generic.CreateView):
	model = Server
	form_class = ServerCreateForm

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.object = None

	def form_valid(self, form):
		rack = RackHelper(Rack.objects.get(pk=self.kwargs.get('pk')))

		try:
			form.instance.position = rack.get_free_position(
				form.instance,
				range(rack.rack.size - form.cleaned_data.get('length') + 1)
			)
			self.object = form.save()
		except NoFreePositionOnRackError:
			messages.error(self.request, 'Сервер не добавлен. Нет свободного места')

		return HttpResponseRedirect(self.get_url())

	def form_invalid(self, form):
		messages.error(self.request, form.errors)
		return HttpResponseRedirect(self.get_url())

	def get_url(self):
		return reverse_lazy('rack_detail', kwargs={'pk': self.kwargs.get('pk')})


class ServerNoteCreateView(LoginRequiredMixin, generic.UpdateView):
	form_class = ServerNoteForm
	model = Server

	def get_success_url(self):
		return reverse_lazy('rack_detail', kwargs={'pk': self.object.rack_id})


class ServerUpdatePositionView(LoginRequiredMixin, generic.UpdateView):
	model = Server
	form_class = ServerUpdatePositionForm

	def form_invalid(self, form):
		messages.error(self.request, 'Сервер не перемещен. Убедитесь в наличии свободного пространства.')
		return HttpResponseRedirect(self.get_success_url())

	def get_success_url(self):
		return reverse_lazy('rack_detail', kwargs={'pk': self.object.rack_id})


class ServerDeleteView(LoginRequiredMixin, generic.DeleteView):
	model = Server

	def get_success_url(self):
		return reverse_lazy('rack_detail', kwargs={'pk': self.object.rack_id})


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


class LinkPortDeleteView(LoginRequiredMixin, generic.DeleteView):
	model = LinkPort

	def delete(self, request, *args, **kwargs):
		LinkPort.objects.filter(port1_id__in=[self.kwargs.get('pk1'), self.kwargs.get('pk2')]).delete()
		return HttpResponseRedirect(self.get_success_url())

	def get_success_url(self):
		return reverse_lazy('server_detail', kwargs={'pk': self.kwargs.get('pk')})
