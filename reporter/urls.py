from django.urls import path
from .views import *

urlpatterns = [
    path('publisher/', PublisherViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('publisher/<int:pk>/', PublisherViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy', 'patch': 'partial_update'})),
    path('publisher-execution/', PublisherExecutionViewSet.as_view({'get': 'list', 'post': 'create'})),
    # Add more paths here as needed
]