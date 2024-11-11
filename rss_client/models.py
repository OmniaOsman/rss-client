from django.db import models
from accounts.models import User
import re


def arabic_slugify(str):
    """
    Custom slugify function that handles Arabic text by transliterating Arabic characters
    to their closest English representation.
    """
    arabic_map = {
        'ا': 'a', 'ب': 'b', 'ت': 't', 'ث': 'th', 'ج': 'j', 'ح': 'h', 'خ': 'kh',
        'د': 'd', 'ذ': 'th', 'ر': 'r', 'ز': 'z', 'س': 's', 'ش': 'sh', 'ص': 's',
        'ض': 'd', 'ط': 't', 'ظ': 'z', 'ع': 'a', 'غ': 'gh', 'ف': 'f', 'ق': 'q',
        'ك': 'k', 'ل': 'l', 'م': 'm', 'ن': 'n', 'ه': 'h', 'و': 'w', 'ي': 'y',
        'ة': 'h', 'ى': 'a', 'ء': 'a', 'ؤ': 'o', 'ئ': 'e', 'إ': 'e', 'أ': 'a',
        'آ': 'a', 'ض': 'd', 'ص': 's', 'ث': 'th', 'ق': 'q', 'ف': 'f', 'غ': 'gh',
        'ع': 'a', 'ه': 'h', 'خ': 'kh', 'ح': 'h', 'ج': 'j', 'ش': 'sh', 'س': 's',
        'ي': 'y', 'ب': 'b', 'ل': 'l', 'ا': 'a', 'ت': 't', 'ن': 'n', 'م': 'm',
        'ك': 'k', 'ط': 't', 'ذ': 'th', 'ء': 'a', 'ؤ': 'o', 'ر': 'r', 'ى': 'a',
        'ة': 'h', 'و': 'w', 'ز': 'z', 'ظ': 'z',
    }
    
    # Convert Arabic characters to English representations
    str = ''.join(arabic_map.get(char, char) for char in str)
    
    # Remove non-word characters and convert spaces to hyphens
    str = re.sub(r'[^\w\s-]', '', str).strip().lower()
    str = re.sub(r'[-\s]+', '-', str)
    
    return str or 'untitled'


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True, help_text='tag name')
    slug = models.SlugField(max_length=100, unique=True, help_text='tag slug')
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = arabic_slugify(self.name)
        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.name
    
    
class Feed(models.Model):
    title = models.CharField(max_length=500, help_text='feed title')
    url = models.URLField(max_length=5000, unique=True, help_text='rss url')
    description = models.TextField(null=True, help_text='feed description')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='feeds', null=True, help_text='user associated with the feed')
    tags = models.ManyToManyField(Tag, related_name='feeds', help_text='tags associated with the feed')
    active = models.BooleanField(default=True, help_text='feed is still active or not')
    external_id = models.CharField(max_length=5000, unique=True, help_text='ID from the original news source')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'url')
        indexes = [
            models.Index(fields=['user', 'url'], name='user_url_index'),
        ]
        
    def str(self):
        return self.title
    
    
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
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_queries', help_text='user associated with the query')
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
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversation_logs', help_text='user associated with the conversation log')
    message = models.TextField(help_text='conversation message')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.message
