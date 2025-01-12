from django.shortcuts import render
from .serializers import PublisherSerializer, PublisherExecutionSerializer
from .models import Publisher, PublisherExecution
from rest_framework import viewsets, permissions
from .hooks import execute_publisher
# Create your views here.
class PublisherViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing Publisher instances.
    """
    serializer_class = PublisherSerializer
    queryset = Publisher.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['user']
    
    def get_queryset(self):
        user = self.request.user
        return Publisher.objects.filter(user=user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        
    def perform_update(self, serializer):
        serializer.save(user=self.request.user)
        
    def partial_update(self, request,pk):
        #get the article id from the request
        article_id = request.data.get('article_id')
        #get the publisher id from the request
        user = self.request.user.id
        execute_publisher(pk, user, article_id)
        return super().partial_update(request, pk)
    
        
    def perform_destroy(self, instance):
        instance.delete()
        
    def get_serializer_context(self):
        return {'request': self.request}
    
class PublisherExecutionViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing PublisherExecution instances.
    """
    serializer_class = PublisherExecutionSerializer
    queryset = PublisherExecution.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['user']
    
    def get_queryset(self):
        user = self.request.user
        return PublisherExecution.objects.filter(user=user)
        
    def get_serializer_context(self):
        return {'request': self.request}