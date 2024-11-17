from rest_framework.views import APIView
from rss_client.logic import get_news_from_multiple_sources, get_tags, summarize_feeds_by_day
from rest_framework import status, response as rest_response
from rest_framework.permissions import IsAuthenticated
from rss_project.utils import process_request
from .serializers import FeedResponseSerializer


class FeedsAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return process_request(
            None,
            FeedResponseSerializer,
            get_news_from_multiple_sources,
            request
        )
    
    
class TagsList(APIView):
    def get(self, request):
        response = get_tags()
        return rest_response.Response(response, status=status.HTTP_200_OK)


class SummaryAPI(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        response = summarize_feeds_by_day(request.query_params, request)
        return rest_response.Response(response, status=status.HTTP_200_OK)
