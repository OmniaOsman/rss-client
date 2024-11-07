from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import AbstractUser


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True, help_text='tag name')
    slug = models.SlugField(max_length=100, unique=True, help_text='tag slug')
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.name
    
    
class Feed(models.Model):
    title = models.CharField(max_length=500, help_text='feed title')
    url = models.URLField(unique=True, help_text='rss url')
    description = models.TextField(null=True, help_text='feed description')
    user = models.ForeignKey('User', on_delete=models.SET_NULL, related_name='feeds', null=True, help_text='user associated with the feed')
    tags = models.ManyToManyField(Tag, related_name='feeds', help_text='tags associated with the feed')
    active = models.BooleanField(default=True, help_text='feed is still active or not')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'url')
        indexes = [
            models.Index(fields=['user', 'url'], name='user_url_index'),
        ]
        
    def str(self):
        return self.title


class User(AbstractUser):
    first_name = models.CharField(max_length=100, help_text='first name')
    user_name = models.CharField(max_length=100, help_text='user name')
    last_name = models.CharField(max_length=100, help_text='last name')
    email = models.EmailField(unique=True, help_text='email address')    
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Source(models.Model):
    name = models.CharField(max_length=100, help_text='source name')
    rss_url = models.URLField(help_text='source url')
    language_code = models.CharField(max_length=100, null=True, help_text='source language')
    created_at = models.DateTimeField(auto_now_add=True) 

    def __str__(self):
        return self.name
    

class Group(models.Model):
    name = models.CharField(max_length=100, help_text='group name')
    sources = models.ManyToManyField(Source, related_name='group', help_text='sources associated with the group')
    user = models.ForeignKey('User', on_delete=models.SET_NULL, related_name='group', null=True, help_text='user associated with the group')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    
class ProcessedFeed(models.Model):
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE, related_name='processed_feeds', help_text='feed associated with the processed feed')
    title = models.CharField(max_length=500, help_text='processed feed title')
    summary = models.TextField(help_text='processed feed summary')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title


class Report(models.Model):
    summary = models.TextField(help_text='report summary')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return str(self.created_at)


class UserQuery(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='user_queries', help_text='user associated with the query')
    question = models.TextField(help_text='query question')
    answer = models.TextField(help_text='query answer')
    date_range_start = models.DateField(verbose_name="Date Range Start")
    date_range_end = models.DateField(verbose_name="Date Range End")
    tags = models.JSONField(null=True, default=list, help_text='query tags')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.question


class ConversationLog(models.Model):
    query = models.ForeignKey('UserQuery', on_delete=models.CASCADE, related_name='conversation_logs', help_text='query associated with the conversation log')
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='conversation_logs', help_text='user associated with the conversation log')
    message = models.TextField(help_text='conversation message')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.message
