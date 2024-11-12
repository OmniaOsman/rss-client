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
        {"role": "user", "content": "extract news tags from the following news without any signs or numbers and put a comma between , each tag"},
        {"role": "user", "content": f"the title: {title}، the summary: {summary}"}
    ]

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=messages
    )
    keywords = response.choices[0].message['content'].strip().split(", ")
    return keywords

    
def fetch_news_from_rss(rss_url: str, limit: int, user_id: int = None):
    feed = feedparser.parse(rss_url)
        
    # Fetch all existing feeds
    existing_feeds = Feed.objects.filter(
        external_id__in=[entry['id'] for entry in feed.entries[:limit]],
        user_id=user_id
    ).prefetch_related('tags')
    
    # Create a dictionary to store existing feeds for efficient lookup
    existing_feeds_dict = {feed.external_id: feed for feed in existing_feeds}
    
    unique_tags = set()
    
    for entry in feed.entries[:limit]: 
        # Generate more tags with OpenAI
        generated_tags = generate_tags_for_feed(entry.title, entry.summary)
        if entry.get('tags', []):
            generated_tags.append(entry.get('tags')[0].get('term'))
        unique_tags.update(generated_tags)
        
        print(generated_tags)
        
        # create new tags 
        new_tags = [tag for tag in unique_tags if not Tag.objects.filter(name=tag).exists()]
        tag_objects = []
        for tag in new_tags:
            tag_obj, created = Tag.objects.get_or_create(name=tag)
            tag_objects.append(tag_obj)
                
        # store the news in the Feed model
        if entry['id'] not in existing_feeds_dict:
            feed_obj = Feed.objects.create(
                external_id=entry['id'],
                title=entry['title'],
                url=entry['link'],
                description=entry.get('summary', ''),
                active=True,
                user_id=user_id
            )
            feed_obj.tags.set(Tag.objects.filter(name__in=generated_tags))
            existing_feeds_dict[entry['id']] = feed_obj
        else:
            # update existing feed
            feed_obj = existing_feeds_dict[entry['id']]
    
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
        
    return {
        'success': True,
        'message': 'News fetched successfully',
        'payload':  all_news
    }
    

def get_tags():
    """Retrieve all unique tags collected.

    Returns:
        list: Unique list of tags
    """
    return list(set(tags))
