import feedparser
import openai
from django.conf import settings
from .models import User


tags = []
openai.api_key = settings.OPENAI_API_KEY


def gpt_35_api(title: str, summary: str):
    """
    Use the GPT-4o-mini model on the OpenAI API to generate a single keyword as a tag for a given news article.

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


def fetch_news_from_rss(rss_url, limit):
    """
    Fetch news from a given RSS source and add tags if not present.

    Args:
        rss_url (str): URL of the RSS source
        limit (int): Number of entries to fetch

    Returns:
        list: A list of news entries
    """
    feed = feedparser.parse(rss_url)
        
    for entry in feed.entries[:limit]:        
        if entry.get('tags', []):
            tags.append(entry.get('tags')[0].get('term'))
        else:
            # Generate tags with OpenAI if not present
            ai_generated_tags = gpt_35_api(entry.title, entry.summary)
            tags.extend(ai_generated_tags)
            
    return feed.entries[:limit]


def get_news_from_multiple_sources():
    """Fetch news from multiple RSS sources and add tags.

    Returns:
        dict: A dictionary with source names as keys and news entries as values
    """
    rss_urls = {
        'AlJazeera': "https://www.ajnet.me/aljazeerarss/a7c186be-1baa-4bd4-9d80-a84db769f779/73d0e1b4-532f-45ef-b135-bfdff8b8cab9",
        'RT': "https://arabic.rt.com/rss/",
        'UN': 'https://news.un.org/feed/subscribe/ar/news/all/rss.xml'
    }

    all_news = {}
    limit = 10
    for source, url in rss_urls.items():
        news_entries = fetch_news_from_rss(url, limit)
        all_news[source] = news_entries

    return all_news


def get_tags():
    """Retrieve all unique tags collected.

    Returns:
        list: Unique list of tags
    """
    return list(set(tags))


def add_feed_to_user(data, request):
    rss_url:str = data['rss_url']
    user:User = request.user
    
    # check rss url and get feed data using feedparser
    try:
        feed = feedparser.parse(rss_url)
        title = feed['feed']['title']
        url = feed.url
        language_code = feed['feed']['language']
    except Exception as e:
        return {
            'success': False,
            'message': str(e)
        }
    
    if user.feed and user.feed.url == rss_url:
        return
    
    # add feed to user
    user.feed.url = url
    user.feed.title = title
    user.feed.language_code = language_code
    user.feed.save()
    