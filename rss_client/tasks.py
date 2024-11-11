from datetime import datetime, timedelta
from celery import shared_task
import feedparser
from .logic import gpt_35_api
from .models import Feed, Tag


@shared_task
def fetch_news_from_rss(rss_url: str, limit: int, user_id: int = None):
    feed = feedparser.parse(rss_url)
        
    for entry in feed.entries[:limit]:  
        filter_feed = (
            {'external_id':entry['id']} if not user_id 
            else {'external_id':entry['id'], 'user_id':user_id}
        )
        feed_obj = Feed.objects.filter(**filter_feed)
        if feed_obj.exists():
            continue
        
        tag = ''
        if entry.get('tags', []):
            tag = entry.get('tags')[0].get('term')
        else:
            # Generate tags with OpenAI if not present
            ai_generated_tags = gpt_35_api(entry.title, entry.summary)
            tag = ai_generated_tags[0]

        # store the tag in the Tag model if not present
        tag_obj, created = Tag.objects.get_or_create(name=tag)
            
        # store the news in the Feed model
        if not Feed.objects.filter(**filter_feed).exists():
            feed_obj = Feed.objects.create(
                external_id=entry['id'],
                title=entry['title'],
                url=entry['link'],
                description=entry.get('title_detail', {}).get('value'),
                active=True,
                user_id=user_id
            )
            feed_obj.tags.set([tag_obj.id])
        
        # make feeds that are from 15 minutes ago inactive
        Feed.objects.filter(
            created_at__lt=datetime.now() - timedelta(minutes=15)
        ).update(active=False)
        
    return feed.entries[:limit]