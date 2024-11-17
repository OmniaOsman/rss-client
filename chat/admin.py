from django.contrib import admin
from .models import UserQuery, ConversationLog

# Register your models here.
admin.site.register(UserQuery)
admin.site.register(ConversationLog)
