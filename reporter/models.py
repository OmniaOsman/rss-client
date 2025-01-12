from django.db import models
from accounts.models import User
from rss_client.models import ProcessedFeed
# Publisher model : acts as publishing method for the article
class Publisher(models.Model):
    # publisher name
    name = models.CharField(max_length=255)
    # type of publisher, should be one of the following
    # discord, email, telegram, webhooks
    type = models.CharField(choices=(
        ('discord', 'Discord'),
        ('email', 'Email'),
        ('telegram', 'Telegram'),
        ('webhooks', 'Webhooks')), max_length=255)
    # publisher parameters, should be a JSON object
    parameters = models.JSONField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='publishers')

    def __str__(self):
        return self.name
    
class PublisherExecution(models.Model):
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE, related_name='executions')
    article = models.ForeignKey(ProcessedFeed, on_delete=models.CASCADE, related_name='publishers')
    #add text field with choices for the status of the execution
    success = models.BooleanField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='publisher_executions')

    def __str__(self):
        return f'{self.publisher.name} - {self.article.title}'