from django.db import models
from django.contrib.auth.models import AbstractUser


class Tags(models.Model):
    name = models.CharField(max_length=100, unique=True, help_text='tag name')
    slug = models.SlugField(max_length=100, unique=True, help_text='tag slug')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    
class Feed(models.Model):
    title = models.CharField(max_length=500, help_text='feed title')
    url = models.URLField(unique=True, help_text='rss url')
    created_at = models.DateTimeField(auto_now_add=True)
    language_code = models.CharField(null=True , help_text='feed language')
    tags = models.ManyToManyField(Tags, related_name='feeds', help_text='tags associated with the feed')
    
    def str(self):
        return self.title


class User(AbstractUser):
    first_name = models.CharField(max_length=100, help_text='first name')
    user_name = models.CharField(max_length=100, help_text='user name')
    last_name = models.CharField(max_length=100, help_text='last name')
    email = models.EmailField(unique=True, help_text='email address')    
    created_at = models.DateTimeField(auto_now_add=True)
    feed = models.ForeignKey(Feed, on_delete=models.SET_NULL, related_name='users', null=True, help_text='feeds associated with the user')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    def str(self):
        return f'{self.first_name} {self.last_name}'
