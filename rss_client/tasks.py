from datetime import datetime
from celery import shared_task
from .models import ProcessedFeed


@shared_task(name='summarize_feeds')
def summarize_feeds(titles, descriptions, urls):
    from rss_client.logic import generate_summary
    print("Hello")
    result = generate_summary(titles, descriptions, urls)
    
    print("summary", result)
    
    # ProcessedFeed.objects.create(
    #     title=title,
    #     summary=summary,
    #     created_at=datetime.now()
    # )
    
    return result
    
