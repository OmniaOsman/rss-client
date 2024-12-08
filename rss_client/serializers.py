from rest_framework import serializers
from accounts.models import User
from rss_project.utils import ResponseSerializer
from rss_client.models import Subscriber, ProcessedFeed
from datetime import datetime


class FeedResponseSerializer(ResponseSerializer):
    payload = serializers.JSONField()


class SubscribeRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, attrs):
        # check that the email in user model
        user = User.objects.filter(email=attrs["email"])
        if not user.exists():
            raise serializers.ValidationError({"email": "You are not registered"})
        if Subscriber.objects.filter(user=user.first(), is_active=True).exists():
            raise serializers.ValidationError({"email": "Subscriber already exists"})
        return attrs


class SubscribeResponseSerializer(ResponseSerializer):
    pass


class UnsubscribeRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, attrs):
        # check that the email in user model
        user = User.objects.filter(email=attrs["email"])
        if not user.exists():
            raise serializers.ValidationError({"email": "You are not registered"})
        subscriber = Subscriber.objects.filter(user=user.first())
        if not subscriber.exists():
            raise serializers.ValidationError({"email": "Subscriber does not exist"})
        if not subscriber.first().is_active:
            raise serializers.ValidationError({"email": "already unsubscribed"})
        return attrs


class UnsubscribeResponseSerializer(ResponseSerializer):
    pass


class SummaryRequestSerializer(serializers.Serializer):
    day_date = serializers.DateField(default=datetime.now().strftime("%Y-%m-%d"))


class SummaryByIDRequestSerializer(serializers.Serializer):
    summary_id = serializers.IntegerField(required=False)

    def validate_summary_id(self, summary_id):
        if not ProcessedFeed.objects.filter(id=summary_id):
            raise serializers.ValidationError("summary_id Not Found")
