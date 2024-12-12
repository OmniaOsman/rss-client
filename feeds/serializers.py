from rss_project.utils import ResponseSerializer
from rest_framework import serializers
from rss_client.models import Feed


class TagSerializer(serializers.Serializer):
    tag_id = serializers.ListField(child=serializers.IntegerField(), required=False)
    name = serializers.ListField(child=serializers.CharField(), required=False)
    
    
class DynamicFilter(serializers.Serializer):
    tags = TagSerializer(many=True, required=False)
    
    
class FeedsSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    url = serializers.URLField(required=False)
    tag = serializers.ListField(child=serializers.CharField(), required=False)
    user_id = serializers.IntegerField(required=False, allow_null=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    group_id = serializers.IntegerField(required=False, allow_null=True)
    description = serializers.CharField(required=False)
    title = serializers.CharField(required=False)
    tags = serializers.ListField(child=serializers.CharField(), required=False)

    
# ---------------------------------- GET Serializer ----------------------------------
class FeedsSerializerGetRequest(serializers.Serializer):
    tags = serializers.ListField(required=False)
    
    
class FeedSerializerGetRequest(serializers.Serializer):
    feed_id = serializers.IntegerField(required=False)
    
    def validate_feed_id(self, value):
        if not Feed.objects.filter(id=value).exists():
            raise serializers.ValidationError("Feed does not exist")
        return value
    
    
class FeedsSerializerGetResponse(ResponseSerializer):
    def __init__(self, *args, **kwargs):
        # Call the parent constructor
        super().__init__(*args, **kwargs)
        
        # Access the data from the serializer context
        data = kwargs.get('data', {})
        
        # Conditionally set the `many` argument based on the input
        if isinstance(data.get('payload'), list):
            self.fields['payload'] = FeedsSerializer(many=True, required=False)
        else:
            self.fields['payload'] = FeedsSerializer(many=False, required=False)
            

class DynamicFilterGetResponse(ResponseSerializer):
    payload = DynamicFilter(many=True)