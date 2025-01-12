from .models import Publisher, PublisherExecution
from rss_client.models import ProcessedFeed
from requests import post
def send_email(publisher,article):
    # This function should send an email with the given article
    pass

def send_telegram_message(publisher,article):
    # This function should send a telegram message with the given article
    pass

def send_discord_message(publisher,article):
    # This function should send a discord message with the given article
    #first we validate the parameters
    if not publisher.parameters.get('webhook_url'):
        raise ValueError('Webhook URL is required')
    #send the message
    response = post(publisher.parameters['webhook_url'], json={'content': article.title})
    if response.status_code != 200:
        return False
    return True
    

def execute_publisher(publisher_id: int,user_id:int,article_id:int):
    # This function should execute the  
    # publisher with the given article
    #get the article
    publisher = Publisher.objects.filter(id=publisher_id, user=user_id)
    if not publisher:
        raise ValueError('Publisher not found')
    publisher = publisher.first()
    article = ProcessedFeed.objects.filter(id=article_id, user=user_id)
    if not article:
        raise ValueError('Article not found')
    article = article.first()
    exec= report_to_publisher(publisher,article)
    if not exec:
        return PublisherExecution.objects.create(publisher=publisher, article=article, user=publisher.user, success=False, message='Failed to publish')
    return PublisherExecution.objects.create(publisher=publisher, article=article, user=publisher.user, success=True, message='Published successfully')

def report_to_publisher(publisher,article):
    # This function should report the summaries to the publishers
    if publisher.type == 'email':
        exec = send_email(publisher,article)
    elif publisher.type == 'telegram':
        exec = send_telegram_message(publisher,article)
    elif publisher.type == 'discord':
        exec = send_discord_message(publisher,article)
    else:
        raise ValueError('Invalid publisher type')
    return exec