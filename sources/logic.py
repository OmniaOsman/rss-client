from sources.models import Source
from rest_framework.exceptions import ValidationError
import feedparser


def get_sources(data, request):
    """
    Get a list of all the sources associated with the current user
    """
    user_id: int = request.user.id
    sources = list(Source.objects.filter(user_id=user_id).values())
    print(sources)
    return {
        'success': True,
        'message': 'Sources fetched successfully',
        'payload':  sources
    }
    
    
def retrive_source(data, request):
    """
    Retrieve a single source by its id
    """
    source = Source.objects.get(id=request.data['source_id'])

    return {
        'success': True,
        'message': 'Source fetched successfully',
        'payload':  source.__dict__
    }
    

def add_source(data, request):
    """
    Add a new RSS source to the database. 
    The request data should contain the 'url' key with the RSS URL 
    and the 'group_id' key with the group id to associate the feed with.
    """
    rss_url: str = data['url']
    group_id: int = data.get('group_id')
    user_id: int = request.user.id

    # check rss url and get feed data using feedparser
    try:
        feed = feedparser.parse(rss_url)
        title = feed['feed']['title']
        url = feed.url
        language_code = feed['feed']['language']
    except Exception as e:
        raise ValidationError('Invalid RSS URL')

    # save the source to the database
    source_obj = Source.objects.create(
        name=title,
        url=url,
        language_code=language_code,
        user_id=user_id,
        group_id=group_id
    )

    return {
        'success': True,
        'message': 'Source added successfully',
        'payload': source_obj.__dict__,
    }
 
 
def edit_source(data, request):
    """
    Edit an existing source by its id.
    """
    source_id = request.data['source_id']
    group_id = data.get('group_id') 
    
    updated_dict = {'id': source_id}
    if group_id:
        updated_dict['group_id'] = group_id
    
    # update the source
    source_obj = Source.objects.filter(id=source_id)
    source_obj.update(**updated_dict)
    
    return {
        'success': True,
        'message': 'Source updated successfully',
        'payload': source_obj.first().__dict__,
    }
    
    
def delete_source(data, request):
    """
    Delete an existing source by its id.
    """
    Source.objects.filter(id=request.data['source_id']).delete()
    
    return {
        'success': True,
        'message': 'Source deleted successfully',
    }    
