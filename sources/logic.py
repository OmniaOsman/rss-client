from sources.models import Source
from rest_framework.exceptions import ValidationError
import feedparser


def get_sources(data, request):
    user_id: int = request.user.id
    id: int = data.get('id')
    
    filter_dict = {'user_id': user_id}
    if id:
        filter_dict['id'] = id
        
    sources = Source.objects.filter(**filter_dict)
    
    

def add_source(data, request):
    rss_url: str = data['rss_url']
    
    # check rss url and get feed data using feedparser
    try:
        feed = feedparser.parse(rss_url)
        title = feed['feed']['title']
        url = feed.url
        language_code = feed['feed']['language']
    except Exception as e:
        raise ValidationError('Invalid RSS URL')
    
    # check if source already exists
    if Source.objects.filter(rss_url=rss_url).exists():
        raise ValidationError('RSS URL already exists')
    
    # save the source to the database
    source_obj = Source.objects.create(
        name=title,
        rss_url=url,
        language_code=language_code
    )
    
    return {
        'success': True,
        'message': 'Feed added successfully',
        'payload': source_obj.__dict__,
    }
    