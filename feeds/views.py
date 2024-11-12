from rest_framework.viewsets import ModelViewSet
from rss_project.utils import process_request, process_query_params
from .logic import get_feeds, retrive_feed, get_dynamic_filter
from feeds.serializers import (
    FeedsSerializerGetRequest,
    FeedsSerializerGetResponse, 
    FeedSerializerGetRequest,
    DynamicFilterGetResponse,

)
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated


class FeedsAPI(ModelViewSet):
    permission_classes = [IsAuthenticated]
    
    @extend_schema(responses=FeedsSerializerGetResponse)
    def list(self, request):
        request_data = request.query_params.copy()
        request_data = process_query_params(request.query_params)
        request._full_data = request_data

        return process_request(
            FeedsSerializerGetRequest,
            FeedsSerializerGetResponse,
            get_feeds,
            request,
            # use_query_params=True | Do not need it due do change in request
        )

    @extend_schema(request=FeedSerializerGetRequest, responses=FeedsSerializerGetResponse)
    def retrieve(self, request, feed_id):
        request_data = request.data.copy()
        request_data['feed_id'] = feed_id
        request._full_data = request_data
        
        return process_request(
            FeedSerializerGetRequest,
            FeedsSerializerGetResponse,
            retrive_feed,
            request
        )
        

class DynamicFilterAPI(ModelViewSet):
    permission_classes = []
    
    def list(self, request):
        return process_request(
            None, 
            DynamicFilterGetResponse,
            get_dynamic_filter,
            request
        )
    