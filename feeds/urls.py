from django.urls import path
from . import views

urlpatterns = [
    path('', views.FeedsAPI.as_view({'get': 'list'}), name='feeds'),
    path('<int:feed_id>', views.FeedsAPI.as_view({'get': 'retrieve'}), name='feed'),
    path('filters', views.DynamicFilterAPI.as_view({'get': 'list'}), name='filters')
]