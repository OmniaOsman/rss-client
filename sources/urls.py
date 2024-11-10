from django.urls import path
from . import views


urlpatterns = [
    path('', views.SourcesAPI.as_view({'post': 'post', 'get': 'list'}), name='sources'),
    path('<int:source_id>', views.SourcesAPI.as_view({'get': 'retrieve', 'patch': 'patch', 'delete': 'destroy'}), name='source'),
]
