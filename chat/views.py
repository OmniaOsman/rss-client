# # views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from .logic import test_internationalization
# from .models import UserQuery, ConversationLog
# # from .serializers import UserQuerySerializer, ConversationLogSerializer
# from rest_framework.permissions import IsAuthenticated

# class UserQueryViewSet(viewsets.ModelViewSet):
#     queryset = UserQuery.objects.all()
#     # serializer_class = UserQuerySerializer
#     permission_classes = [IsAuthenticated]  

#     def perform_create(self, serializer):
#         # Automatically associate the current user with the query
#         serializer.save(user=self.request.user)

# class ConversationLogViewSet(viewsets.ModelViewSet):
#     queryset = ConversationLog.objects.all()
#     # serializer_class = ConversationLogSerializer
#     permission_classes = [IsAuthenticated]

#     def perform_create(self, serializer):
#         # Associate the user with the conversation log
#         serializer.save(user=self.request.user)

class Test(APIView):
    def get(self, request):
        response = test_internationalization()
        return Response(response)