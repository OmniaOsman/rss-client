from django.urls import path
from . import views


urlpatterns = [
    path('', views.SourcesAPI.as_view(), name='sources'),
]
