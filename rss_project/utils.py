from rest_framework import serializers


class ResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    message = serializers.CharField()
