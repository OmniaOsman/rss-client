from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    first_name = models.CharField(max_length=100, help_text='first name', null=True)
    last_name = models.CharField(max_length=100, help_text='last name', null=True)
    username = models.CharField(max_length=100, help_text='user name')
    email = models.EmailField(unique=True, help_text='email address')    
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    def __str__(self):
        return f'{self.first_name} {self.last_name}'
    