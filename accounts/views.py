from rest_framework.views import APIView
from .serializers import *
from .logic import register_user, login_user
from drf_spectacular.utils import extend_schema
from rss_project.utils import process_request


class RegisterView(APIView):
    permission_classes = []
    
    @extend_schema(request=RegisterSerializer, responses=RegisterSerializerResponse)
    def post(self, request):
        return process_request(
            RegisterSerializer,
            RegisterSerializerResponse,
            register_user,
            request
        )

class LoginView(APIView):
    permission_classes = []
    
    @extend_schema(request=LoginSerializer, responses=LoginSerializerResponse)
    def post(self, request):
        return process_request(
            LoginSerializer,
            LoginSerializerResponse,
            login_user,
            request
        )
        