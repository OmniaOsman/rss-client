from rest_framework import serializers
from rss_project.utils import ResponseSerializer


class AskQuestionRequest(serializers.Serializer):
    question = serializers.CharField()
    date_range_start = serializers.DateField(required=False)
    date_range_end = serializers.DateField(required=False)


class AskQuestionResponse(ResponseSerializer):
    payload = serializers.CharField()
