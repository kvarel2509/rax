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
	RackCreateBackSideView, LinkPortDeleteView,
)

from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path, include


urlpatterns = [
	path('', RackListView.as_view(), name='rack_list'),
	path('rack/', include([
		path('create/', RackCreateView.as_view(), name='rack_create'),
		path('<int:pk>/', RackDetailView.as_view(), name='rack_detail'),
		path('<int:pk>/delete/', RackDeleteView.as_view(), name='rack_delete'),
		path('<int:pk>/update/', RackUpdateView.as_view(), name='rack_update'),
		path('<int:pk>/add-backside/', RackCreateBackSideView.as_view(), name='rack_add_backside')
	])),
	path('server/', include([
		path('<int:pk>/', ServerDetailView.as_view(), name='server_detail'),
		path('create/<int:pk>', ServerCreateView.as_view(), name='server_create'),
		path('<int:pk>/delete/', ServerDeleteView.as_view(), name='server_delete'),
		path('<int:pk>/update/', ServerUpdateView.as_view(), name='server_update'),
		path('<int:pk>/delete_ports/', PortDeleteView.as_view(), name='ports_delete'),
		path('<int:pk>/server_note_create/', ServerNoteCreateView.as_view(), name='server_note_create'),
		path('<int:pk>/create_port/', PortCreateView.as_view(), name='port_create'),
		path('<int:pk>/move/', MoveServerView.as_view(), name='server_move'),
		path('<int:pk>/<int:pk1>-<int:pk2>/link-delete/', LinkPortDeleteView.as_view(), name='link_delete')
	])),
	path('port/', include([
		path('<int:pk>/update/', PortUpdateView.as_view(), name='port_update'),
	])),
	path('accounts/', include([
		path('login/', LoginView.as_view(), name='login'),
		path('logout/', LogoutView.as_view(), name='logout'),
	])),
]
