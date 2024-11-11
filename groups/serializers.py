from rest_framework import serializers
from groups.models import Group
from rss_project.utils import ResponseSerializer


class GroupSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    created_at = serializers.DateTimeField(format="%Y-%m-%d")
    user_id = serializers.IntegerField(required=False, allow_null=True)
    
    class Meta:
        model = Group
        fields = ['id', 'name', 'user_id', 'created_at']
        

# ---------------------------------- GET Serializer ----------------------------------
class GroupSerializerGetRequest(serializers.Serializer):
    group_id = serializers.IntegerField(required=False)
    
    def validate_group_id(self, value):
        # check if group exists
        if not Group.objects.filter(id=value).exists():
            raise serializers.ValidationError("Group does not exist")
        return value
    
    
class GroupSerializerGetResponse(ResponseSerializer):
    def __init__(self, *args, **kwargs):
        # Call the parent constructor
        super().__init__(*args, **kwargs)
        
        # Access the data from the serializer context
        data = kwargs.get('data', {})
        
        # Conditionally set the `many` argument based on the input
        if isinstance(data.get('payload'), list):
            self.fields['payload'] = GroupSerializer(many=True, required=False)
        else:
            self.fields['payload'] = GroupSerializer(many=False, required=False)


# ---------------------------------- POST Serializer ----------------------------------
class GroupSerializerPostRequest(serializers.ModelSerializer):    
    class Meta:
        model = Group
        fields = ['name']
        
    def validate_name(self, value):
        # check if group already exists
        if Group.objects.filter(name=value).exists():
            raise serializers.ValidationError("Group already exists")
        return value
        
        
class GroupSerializerPostResponse(ResponseSerializer):
    payload = GroupSerializer()


# ---------------------------------- PUT Serializer ----------------------------------
class GroupSerializerPutRequest(serializers.Serializer):
    group_id = serializers.IntegerField(required=True)
    name = serializers.CharField(required=False)
    
    def validate_group_id(self, value):
        # check if group exists
        if not Group.objects.filter(id=value).exists():
            raise serializers.ValidationError("Group does not exist")
        return value
    

class GroupSerializerPatchResponse(ResponseSerializer):
    payload = GroupSerializer()
    
    
# ---------------------------------- DELETE Serializer ----------------------------------
class GroupSerializerDeleteRequest(serializers.Serializer):
    group_id = serializers.IntegerField(required=True)
    
    def validate_group_id(self, value):
        # check if group exists
        if not Group.objects.filter(id=value).exists():
            raise serializers.ValidationError("Group does not exist")
        return value
    

class GroupSerializerDeleteResponse(ResponseSerializer):
    pass
    