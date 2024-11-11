from django.urls import path
from . import views


urlpatterns = [
    path('', views.GroupsAPI.as_view({'post': 'post', 'get': 'list'}), name='groups'),
    path('<int:group_id>', views.GroupsAPI.as_view({'get': 'retrieve', 'put': 'put', 'delete': 'destroy'}), name='group'),
]
