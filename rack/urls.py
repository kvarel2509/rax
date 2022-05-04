from django.urls import path, include
from .views import *


urlpatterns = [
	path('rack_create/', RackCreateView.as_view(), name='rack_create'),
	path('', RackListView.as_view(), name='rack_list'),
	path('rack_detail/<int:pk>/', RackDetailView.as_view(), name='rack_detail'),
	path('rack_detail/<int:pk>/server_create/', ServerCreateView.as_view(), name='server_create'),
	path('server/<int:pk>/delete/', ServerDeleteView.as_view(), name='server_delete'),
	path('server/<int:pk>/server_note_create/', ServerNoteCreateView.as_view(), name='server_note_create'),
	path('server/<int:pk>/<str:move_type>/', MoveServerView.as_view(), name='server_move'),

]