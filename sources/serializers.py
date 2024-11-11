from rest_framework import serializers
from groups.models import Group
from rss_project.utils import ResponseSerializer
from .models import Source


class SourceSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    user_id = serializers.IntegerField(required=False, allow_null=True)
    group_id = serializers.IntegerField(required=False, allow_null=True)
    
    class Meta:
        model = Source
        fields = ['id', 'name', 'url', 'language_code', 'group_id', 'user_id', 'created_at']
        

# ---------------------------------- GET Serializer ----------------------------------
class SourceSerializerGetRequest(serializers.Serializer):
    source_id = serializers.IntegerField(required=False)
    
    def validate_source_id(self, value):
        # check if source exists
        if not Source.objects.filter(id=value).exists():
            raise serializers.ValidationError("Source does not exist")
        return value
    
    
class SourceSerializerGetResponse(ResponseSerializer):
    def __init__(self, *args, **kwargs):
        # Call the parent constructor
        super().__init__(*args, **kwargs)
        
        # Access the data from the serializer context
        data = kwargs.get('data', {})

        # Conditionally set the `many` argument based on the input
        if isinstance(data.get('payload'), list):
            self.fields['payload'] = SourceSerializer(many=True, required=False)
        else:
            self.fields['payload'] = SourceSerializer(many=False, required=False)


# ---------------------------------- POST Serializer ----------------------------------
class SourceSerializerPostRequest(serializers.ModelSerializer):
    group_id = serializers.IntegerField(required=False)  
    
    class Meta:
        model = Source
        fields = ['url', 'group_id']
        
    def validate(self, attrs):
        user_id = self.context['request'].user.id
        rss_url = attrs['url']
        group_id = attrs.get('group_id')
        
        # check if group_id is present
        if group_id:
            if not Group.objects.filter(id=group_id, user_id=user_id).exists():
                raise serializers.ValidationError('This group does not exist')
            
        # check if source already exists
        if Source.objects.filter(url=rss_url, user_id=user_id).exists():
            raise serializers.ValidationError('This URL already exists')
        
        return attrs
        
        
class SourceSerializerPostResponse(ResponseSerializer):
    payload = SourceSerializer()


# ---------------------------------- PATCH Serializer ----------------------------------
class SourceSerializerPatchRequest(serializers.Serializer):
    source_id = serializers.IntegerField(required=False)
    group_id = serializers.IntegerField(required=False)
    
    def validate_source_id(self, value):
        # check if source exists
        if not Source.objects.filter(id=value).exists():
            raise serializers.ValidationError("Source does not exist")
        return value
    
    def validate_group_id(self, value):
        # check if group exists
        if not Group.objects.filter(id=value).exists():
            raise serializers.ValidationError("Group does not exist")
        return value
    

class SourceSerializerPatchResponse(ResponseSerializer):
    payload = SourceSerializer()
    
    
# ---------------------------------- DELETE Serializer ----------------------------------
class SourceSerializerDeleteRequest(serializers.Serializer):
    source_id = serializers.IntegerField(required=True)
    
    def validate_source_id(self, value):
        # check if source exists
        if not Source.objects.filter(id=value).exists():
            raise serializers.ValidationError("Source does not exist")
        return value
    

class SourceSerializerDeleteResponse(ResponseSerializer):
    pass
    