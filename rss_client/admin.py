from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Feed)
admin.site.register(ProcessedFeed)
admin.site.register(Tag)
admin.site.register(Group)
admin.site.register(UserQuery)
admin.site.register(ConversationLog)
admin.site.register(Report) 