from rest_framework.viewsets import ModelViewSet
from groups.logic import add_group, delete_group, edit_group, get_groups, retrive_group
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from .serializers import (
    GroupSerializerDeleteRequest,
    GroupSerializerDeleteResponse,
    GroupSerializerPutRequest,
    GroupSerializerPostRequest, 
    GroupSerializerPostResponse, 
    GroupSerializerGetResponse,
    GroupSerializerGetRequest
)
from rss_project.utils import process_request


class GroupsAPI(ModelViewSet):
    permission_classes = [IsAuthenticated]
    
    @extend_schema(responses=GroupSerializerGetResponse)
    def list(self, request):
        return process_request(
            None,
            GroupSerializerGetResponse,
            get_groups,
            request
        )
    
    @extend_schema(responses=GroupSerializerGetResponse)
    def retrieve(self, request, group_id):
        # append the group id to request
        request_data = request.data.copy()
        
        # Now you can modify the request data
        request_data['group_id'] = group_id
        
        # Replace the original request.data with your modified version
        request._full_data = request_data
        
        return process_request(
            GroupSerializerGetRequest,
            GroupSerializerGetResponse,
            retrive_group,
            request,
        )
    
    @extend_schema(request=GroupSerializerPostRequest, responses=GroupSerializerPostResponse)
    def post(self, request):
        return process_request(
            GroupSerializerPostRequest,
            GroupSerializerPostResponse,
            add_group,
            request
        )
        
    @extend_schema(responses=GroupSerializerGetResponse)
    def put(self, request, group_id):
        request_data = request.data.copy()
        
        # Now you can modify the request data
        request_data['group_id'] = group_id
        
        # Replace the original request.data with your modified version
        request._full_data = request_data
        
        return process_request(
            GroupSerializerPutRequest,
            GroupSerializerGetResponse,
            edit_group,
            request,
        )
    
    @extend_schema(
        parameters=[], 
        responses={200: GroupSerializerDeleteResponse},
    )
    def destroy(self, request, group_id):
        request_data = request.data.copy()
        request_data['group_id'] = group_id
        request._full_data = request_data
        
        return process_request(
            GroupSerializerDeleteRequest,
            GroupSerializerDeleteResponse,
            delete_group,
            request
        )
    