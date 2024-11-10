from rest_framework.views import APIView
from rss_client.logic import get_news_from_multiple_sources, get_tags
from rest_framework import status, response as rest_response
from rest_framework.permissions import IsAuthenticated
from rss_project.utils import process_request


class NewsList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        response = get_news_from_multiple_sources()
        return rest_response.Response(response, status=status.HTTP_200_OK)
    
    
class TagsList(APIView):
    def get(self, request):
        response = get_tags()
        return rest_response.Response(response, status=status.HTTP_200_OK)
