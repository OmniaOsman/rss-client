from django.urls import path
from . import views

urlpatterns = [
    path('', views.FeedsAPI.as_view(), name='news'),
    path('tags', views.TagsList.as_view(), name='tags'),
    path('summary', views.SummaryAPI.as_view(), name='summary'),
    path('subscribe', views.SubscribeAPI.as_view(), name='subscribe'),
]
