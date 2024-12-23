from rest_framework import serializers
from feeds.serializers import FeedsSerializer
from groups.models import Group
from rss_project.utils import ResponseSerializer
from .models import Source


class SourceSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    user_id = serializers.IntegerField(required=False, allow_null=True)
    group_id = serializers.IntegerField(required=False, allow_null=True)
    feeds = FeedsSerializer(many=True, required=False)
    
    class Meta:
        model = Source
        fields = ['id', 'name', 'url', 'language_code', 'group_id', 'user_id', 'created_at', 'feeds']
        

# ---------------------------------- GET Serializer ----------------------------------
class SourceSerializerGetRequest(serializers.Serializer):
    source_id = serializers.IntegerField(required=False)
    page = serializers.IntegerField(required=False)
    size = serializers.IntegerField(required=False)
    
    def validate_source_id(self, value):
        # check if source exists
        if not Source.objects.filter(id=value).exists():
            raise serializers.ValidationError("Source does not exist")
        return value
    

class PaginationSerializer(serializers.Serializer):
    next_page = serializers.BooleanField(required=False)
    previous_page = serializers.BooleanField(required=False)
    total_pages = serializers.IntegerField(required=False)


class RetriveSourceSerializer(serializers.Serializer):
    data = SourceSerializer(many=False, required=False)
    pagination = PaginationSerializer(many=False, required=False)


class SourceSerializerGetResponse(ResponseSerializer):
    SourceSerializer(many=True, required=False)


class RetrieveSourceSerializerGetResponse(ResponseSerializer):
    payload = RetriveSourceSerializer()


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
    