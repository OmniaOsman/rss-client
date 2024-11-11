from django.db import models
from accounts.models import User
from groups.models import Group


class Source(models.Model):
    name = models.CharField(max_length=100, help_text='source name')
    url = models.URLField(help_text='source url')
    language_code = models.CharField(max_length=100, null=True, help_text='source language')
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, related_name='sources', null=True, help_text='group associated with the source')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='sources', null=True, help_text='user associated with the source')
    created_at = models.DateTimeField(auto_now_add=True) 

    def __str__(self):
        return self.name
    