from django.db import models
from accounts.models import User


class Group(models.Model):
    name = models.CharField(max_length=100, help_text='group name')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='group', null=True, help_text='user associated with the group')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name