from rest_framework.viewsets import ModelViewSet
from sources.logic import add_source, delete_source, edit_source, get_sources, retrive_source
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from .serializers import (
    RetrieveSourceSerializerGetResponse,
    SourceSerializerDeleteRequest,
    SourceSerializerDeleteResponse,
    SourceSerializerPatchRequest,
    SourceSerializerPostRequest, 
    SourceSerializerPostResponse, 
    SourceSerializerGetResponse,
    SourceSerializerGetRequest
)
from rss_project.utils import process_request


class SourcesAPI(ModelViewSet):
    permission_classes = [IsAuthenticated]
    
    @extend_schema(responses=SourceSerializerGetResponse)
    def list(self, request):
        return process_request(
            None,
            SourceSerializerGetResponse,
            get_sources,
            request
        )
    
    @extend_schema(parameters=[SourceSerializerGetRequest], responses=RetrieveSourceSerializerGetResponse)
    def retrieve(self, request, source_id):
        # append the source id to request
        request_data = request.data.copy()
        request_data['source_id'] = source_id
        request_data['page'] = request.query_params.get('page', 1)
        
        request._full_data = request_data
        
        return process_request(
            SourceSerializerGetRequest,
            RetrieveSourceSerializerGetResponse,
            retrive_source,
            request,
        )
    
    @extend_schema(request=SourceSerializerPostRequest, responses=SourceSerializerPostResponse)
    def post(self, request):
        return process_request(
            SourceSerializerPostRequest,
            SourceSerializerPostResponse,
            add_source,
            request
        )
        
    @extend_schema(responses=SourceSerializerGetResponse)
    def patch(self, request, source_id):
        request_data = request.data.copy()
        
        # Now you can modify the request data
        request_data['source_id'] = source_id
        
        # Replace the original request.data with your modified version
        request._full_data = request_data
        
        return process_request(
            SourceSerializerPatchRequest,
            SourceSerializerGetResponse,
            edit_source,
            request,
        )
    
    @extend_schema(
        parameters=[], 
        responses={200: SourceSerializerDeleteResponse},
    )
    def destroy(self, request, source_id):
        request_data = request.data.copy()
        request_data['source_id'] = source_id
        request._full_data = request_data
        
        return process_request(
            SourceSerializerDeleteRequest,
            SourceSerializerDeleteResponse,
            delete_source,
            request
        )
    