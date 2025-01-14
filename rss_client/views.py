from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rss_client.logic import (
    get_news_from_multiple_sources,
    get_tags,
    summarize_feeds_by_day,
    subscribe_to_newsletter,
    unsubscribe_from_newsletter,
    get_summary_by_id,
)
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rss_project.utils import process_request
from .serializers import (
    FeedResponseSerializer,
    UnsubscribeResponseSerializer,
    SubscribeResponseSerializer,
    SummaryRequestSerializer,
    SummaryByIDRequestSerializer,
)
from drf_spectacular.utils import extend_schema


class FeedsAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return process_request(
            None, FeedResponseSerializer, get_news_from_multiple_sources, request
        )


class TagsList(APIView):
    def get(self, request):
        response = get_tags()
        return Response(response, status=status.HTTP_200_OK)


class SummaryAPI(ModelViewSet):
    permission_classes = []

    def list(self, request, uid):
        # append uid of the user to request
        request_data = request.query_params.copy()
        request_data["uid"] = uid
        request._full_data = request_data

        serializer = SummaryRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        response = summarize_feeds_by_day(serializer.validated_data, request)
        return HttpResponse(response, status=status.HTTP_200_OK)

    def retrieve(self, request, summary_id):
        # append the source id to request
        request_data = request.data.copy()
        request_data["summary_id"] = summary_id
        request._full_data = request_data

        serializer = SummaryByIDRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        response = get_summary_by_id(serializer.validated_data, request)
        return HttpResponse(response, status=status.HTTP_200_OK)


