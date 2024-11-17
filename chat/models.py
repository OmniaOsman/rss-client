from django.db import models
from accounts.models import User


class UserQuery(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_queries', help_text='user associated with the query')
    question = models.TextField(help_text='query question')
    answer = models.TextField(help_text='query answer')
    date_range_start = models.DateField(verbose_name="Date Range Start", null=True)
    date_range_end = models.DateField(verbose_name="Date Range End", null=True)
    tags = models.JSONField(null=True, default=list, help_text='query tags')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.question


class ConversationLog(models.Model):
    query = models.ForeignKey('UserQuery', null=True, on_delete=models.CASCADE, related_name='conversation_logs', help_text='query associated with the conversation log')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversation_logs', help_text='user associated with the conversation log')
    message = models.TextField(help_text='conversation message')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.message