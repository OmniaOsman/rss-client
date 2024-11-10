from rest_framework import serializers
from rss_project.utils import ResponseSerializer
from .models import Source


class SourceSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    class Meta:
        model = Source
        fields = ['id', 'name', 'rss_url', 'language_code', 'created_at']
        
        
class SourceSerializerPostRequest(serializers.ModelSerializer):    
    class Meta:
        model = Source
        fields = ['rss_url']
        
        
class SourceSerializerPostResponse(ResponseSerializer):
    payload = SourceSerializer()
