from django.urls import path
from . import views


urlpatterns = [
    path('', views.ChatAPI.as_view(), name='chat'),
]