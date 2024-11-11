import feedparser
import openai
from django.conf import settings
from sources.models import Source
from .models import Feed, Tag
from rest_framework.validators import ValidationError
from datetime import datetime, timedelta


tags = []
openai.api_key = settings.OPENAI_API_KEY


def generate_tags_for_feed(title: str, summary: str):
    """
    Use the GPT-4o-mini model o.models import Feed, Tagn the OpenAI API to generate a single keyword as a tag for a given news article.

    Args:
        title (str): The title of the news article.
        summary (str): A brief summary of the news article.

    Returns:
        list: A list containing a single element, the generated tag as a string.
    """
    messages = [
        {"role": "system", "content": "You are a helpful assistant that generates keywords."},
        {"role": "user", "content": f"برجاء توليد كلمة واحدة فقط كعلامة (Tag) تلخص الموضوع الرئيسي للخبر بناءً على العنوان والخلاصة التالية:\n\nالعنوان: {title}\nالخلاصة: {summary}\n\nالكلمات المفتاحية:"}
    ]
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=messages
    )
    keywords = response.choices[0].message['content'].strip().split(", ")
    return keywords

    
def fetch_news_from_rss(rss_url: str, limit: int, user_id: int = None):
    feed = feedparser.parse(rss_url)
        
    for entry in feed.entries[:limit]:  
        tag = ''
        if entry.get('tags', []):
            tag = entry.get('tags')[0].get('term')
        else:
            # Generate tags with OpenAI if not present
            ai_generated_tags = generate_tags_for_feed(entry.title, entry.summary)
            tag = ai_generated_tags[0]
            
        # store the tag in the Tag model if not present
        tag_obj, created = Tag.objects.get_or_create(name=tag)
            
        # store the news in the Feed model
        # check if the feed already exists
        filter_feed = {'external_id':entry['id']} if not user_id else {'external_id':entry['id'], 'user_id':user_id}
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


def get_news_from_multiple_sources(data, request):
    user_id: int = request.user.id
    
    # Get sources associated with the user
    sources = Source.objects.filter(user_id=user_id)
    if not sources:
        raise ValidationError('No sources found for this user')
        
    # Get RSS URLs from the sources
    rss_urls = {}
    for source in sources:
        rss_urls[source.name] = source.url
        
    all_news = {}
    limit = 10
    for source, url in rss_urls.items():
        news_entries = fetch_news_from_rss(url, limit, user_id)
        all_news[source] = news_entries
        
    return all_news
    

def get_tags():
    """Retrieve all unique tags collected.

    Returns:
        list: Unique list of tags
    """
    return list(set(tags))
