from .serializers import AskQuestionRequest, AskQuestionResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from .logic import ask_question_v2
from rss_project.utils import process_request
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema


class ChatAPI(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=AskQuestionRequest, responses=AskQuestionResponse)
    def post(self, request):
        return process_request(
            AskQuestionRequest, 
            AskQuestionResponse, 
            ask_question_v2, 
            request
        )


# class Test(APIView):
#     def get(self, request):
#         response = test_internationalization()
#         return Response(response)