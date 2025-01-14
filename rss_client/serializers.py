from rest_framework import serializers
from accounts.models import User
from rss_project.utils import ResponseSerializer
from rss_client.models import ProcessedFeed


class FeedResponseSerializer(ResponseSerializer):
    payload = serializers.JSONField()




class SummaryRequestSerializer(serializers.Serializer):
    uid = serializers.UUIDField(required=False)

    def validate_uid(self, uid):
        if not User.objects.filter(uid=uid).exists():
            raise serializers.ValidationError("User does not exist")
        return uid


class SummaryByIDRequestSerializer(serializers.Serializer):
    summary_id = serializers.IntegerField(required=False)

    def validate_summary_id(self, summary_id):
        if not ProcessedFeed.objects.filter(id=summary_id):
            raise serializers.ValidationError("summary_id Not Found")
