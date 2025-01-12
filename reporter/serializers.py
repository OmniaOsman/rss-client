from .models import Publisher, PublisherExecution
from rest_framework import serializers
class PublisherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publisher
        fields = '__all__'
        
class PublisherExecutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PublisherExecution
        fields = '__all__'
        
    def create(self, validated_data):
        publisher = validated_data['publisher']
        article = validated_data['article']
        user = self.context['request'].user
        execution = PublisherExecution.objects.create(publisher=publisher, article=article, user=user)
        return execution
    
    def validate(self, attrs):
        return super().validate(attrs)