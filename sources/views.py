from rest_framework.views import APIView
from sources.logic import add_source
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from .serializers import SourceSerializerPostRequest, SourceSerializerPostResponse
from rss_project.utils import process_request

# Create your views here.
class SourcesAPI(APIView):
    permission_classes = [IsAuthenticated]
    
    @extend_schema(request=SourceSerializerPostRequest, responses=SourceSerializerPostResponse)
    def post(self, request):
        return process_request(
            SourceSerializerPostRequest,
            SourceSerializerPostResponse,
            add_source,
            request
        )
        