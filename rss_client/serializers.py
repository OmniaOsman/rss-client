from rest_framework import serializers
from rss_project.utils import ResponseSerializer
from rss_client.models import Subscriber


class FeedResponseSerializer(ResponseSerializer):
    payload = serializers.JSONField()



class SubscribeRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, attrs):
        if Subscriber.objects.filter(email=attrs['email'], is_active=True).exists():
            raise serializers.ValidationError({"email": "Subscriber already exists"})
        return attrs
    

class SubscribeResponseSerializer(ResponseSerializer):
    pass


class UnsubscribeRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, attrs):
        subscriber = Subscriber.objects.filter(email=attrs['email'])
        if not subscriber.exists():
            raise serializers.ValidationError({"email": "Subscriber does not exist"})
        if not subscriber.first().is_active:
            raise serializers.ValidationError({"email": "already unsubscribed"})
        return attrs
    

class UnsubscribeResponseSerializer(ResponseSerializer):
    pass