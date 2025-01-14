from django.urls import path
from . import views

urlpatterns = [
    path('', views.FeedsAPI.as_view(), name='news'),
    path('tags', views.TagsList.as_view(), name='tags'),
    path('summary/<int:summary_id>', views.SummaryAPI.as_view({'get': 'retrieve'}), name='summary'),
    path('summary/<str:uid>', views.SummaryAPI.as_view({'get': 'list'}), name='summary'),
]
