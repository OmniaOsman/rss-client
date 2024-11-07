from rest_framework.views import APIView
from .serializers import *
from .logic import register_user, login_user
from rest_framework.response import Response
from rest_framework import status


class RegisterView(APIView):
    permission_classes = []
    
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        response = register_user(serializer.data, request)
        response = RegisterSerializerResponse(data=response)
        response.is_valid(raise_exception=True)
        return Response(response.validated_data, status=status.HTTP_201_CREATED)
    

class LoginView(APIView):
    permission_classes = []
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        response = login_user(serializer.data, request)
        response = LoginSerializerResponse(data=response)
        response.is_valid(raise_exception=True)
        return Response(response.validated_data, status=status.HTTP_200_OK)
        