from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import generic

from .forms import ServerNoteForm, ServerCreateForm, RackCreateForm
from .models import Rack, Server
from .services.rack import RackHelper
from .utils import get_parsing_list, get_new_space_after_move, get_space_after_delete


class RackCreateView(generic.CreateView):
	"""Для создания новой полки"""
	template_name = 'rack/rack_create.html'
	form_class = RackCreateForm

	def form_valid(self, form):
		self.object = form.save(commit=False)
		self.object.space = [self.object.size * 3]
		self.object.size *= 3
		self.object.save()
		return super().form_valid(form)


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
		return context


class ServerCreateView(generic.FormView):
	"""для создания сервера"""
	template_name = 'rack/server_create.html'
	model = Server
	form_class = ServerCreateForm

	def get_space_server(self, form):
		new_space = []
		for index, value in enumerate(self.obj.space):
			if isinstance(value, int) and value >= form.cleaned_data['length']:
				server = Server.objects.create(**form.cleaned_data)
				new_space.extend(
					[{'id': server.pk, 'length': server.length}, value - server.length, *self.obj.space[index + 1:]])
				return get_parsing_list(new_space)
			new_space.append(value)
		return False

	def form_valid(self, form):
		self.obj = get_object_or_404(Rack, pk=self.kwargs['pk'])
		form.cleaned_data['rack'] = self.obj
		new_space = self.get_space_server(form)
		if new_space:
			self.obj.space = new_space
			self.obj.save()
		return super().form_valid(form)

	def get_success_url(self):
		return reverse_lazy('rack_detail', kwargs={'pk': self.kwargs['pk']})


class ServerNoteCreateView(generic.UpdateView):
	"""Для создания заметки на сервер"""
	form_class = ServerNoteForm
	template_name = 'rack/server_note_create.html'
	model = Server

	def get_success_url(self):
		return reverse_lazy('rack_detail', kwargs={'pk': self.object.rack_id})


class MoveServerView(generic.View):
	"""Для перемещения сервера по полке"""

	def get(self, request, pk, move_type, *args, **kwargs):
		server = get_object_or_404(Server, pk=pk)
		space = server.rack.space
		new_space = get_new_space_after_move(server, space, move_type)
		if new_space:
			new_space = get_parsing_list(new_space)
			server.rack.space = new_space
			server.rack.save()
		return redirect(reverse_lazy('rack_detail', kwargs={'pk': server.rack_id}))


class ServerDeleteView(generic.View):

	def get(self, request, pk, *args, **kwargs):
		server = get_object_or_404(Server, pk=pk)
		server.rack.space = get_parsing_list(get_space_after_delete(server))
		server.rack.save()
		pk_for_redirect = server.rack.pk
		server.delete()
		return redirect(reverse_lazy('rack_detail', kwargs={'pk': pk_for_redirect}))
