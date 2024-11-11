from rest_framework import serializers
from rss_project.utils import ResponseSerializer


class FeedResponseSerializer(ResponseSerializer):
    payload = serializers.JSONField()
