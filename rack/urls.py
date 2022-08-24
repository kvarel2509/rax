from .views import (
	RackDetailView,
	RackCreateView,
	RackListView,
	RackDeleteView,
	RackUpdateView,
	ServerCreateView,
	ServerDeleteView,
	ServerNoteCreateView,
	ServerUpdateView,
	MoveServerView,
	ServerDetailView,
	PortUpdateView,
	PortCreateView,
	PortDeleteView,
)

from django.urls import path


urlpatterns = [
	path('', RackListView.as_view(), name='rack_list'),
	path('rack/create/', RackCreateView.as_view(), name='rack_create'),
	path('rack/<int:pk>/', RackDetailView.as_view(), name='rack_detail'),
	path('rack/<int:pk>/delete/', RackDeleteView.as_view(), name='rack_delete'),
	path('rack/<int:pk>/update/', RackUpdateView.as_view(), name='rack_update'),
	path('server/<int:pk>/', ServerDetailView.as_view(), name='server_detail'),
	path('server/create/<int:pk>', ServerCreateView.as_view(), name='server_create'),
	path('server/<int:pk>/delete/', ServerDeleteView.as_view(), name='server_delete'),
	path('server/<int:pk>/update/', ServerUpdateView.as_view(), name='server_update'),
	path('server/<int:pk>/delete_ports/', PortDeleteView.as_view(), name='ports_delete'),
	path('server/<int:pk>/server_note_create/', ServerNoteCreateView.as_view(), name='server_note_create'),
	path('server/<int:pk>/create_port/', PortCreateView.as_view(), name='port_create'),
	path('server/<int:pk>/move/', MoveServerView.as_view(), name='server_move'),
	path('port/<int:pk>/update/', PortUpdateView.as_view(), name='port_update')
]
