from rest_framework.views import APIView
from rss_client.logic import get_news_from_multiple_sources
from rest_framework import status, response as rest_response


class NewsList(APIView):

    def get(self, request):
        response = get_news_from_multiple_sources()
        return rest_response.Response(response, status=status.HTTP_200_OK)