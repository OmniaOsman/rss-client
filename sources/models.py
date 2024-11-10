from django.db import models


class Source(models.Model):
    name = models.CharField(max_length=100, help_text='source name')
    rss_url = models.URLField(help_text='source url')
    language_code = models.CharField(max_length=100, null=True, help_text='source language')
    created_at = models.DateTimeField(auto_now_add=True) 

    def __str__(self):
        return self.name
    