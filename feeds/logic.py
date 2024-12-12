from rss_client.models import Feed
from django.contrib.postgres.aggregates import ArrayAgg


def get_feeds(data, request):
    """
    Get a list of all the feeds associated with the current user
    """
    user_id: int = request.user.id
    tags: list = data.get('tags', [])
    
    filter_feeds = {'user_id': user_id}
    if tags:
        filter_feeds['tags__name__in'] = tags
    
    # Get feeds associated with the user
    feeds = list(
        Feed.objects.filter(**filter_feeds)
        .annotate(tag=ArrayAgg('tags__name', distinct=True))
        .values("title", "url", "description", "id", "tag", "created_at").order_by('tag')
    )
    
    return {
        'success': True,
        'message': 'Feeds fetched successfully',
        'payload':  feeds
    }


def retrive_feed(data, request):
    """
    Retrieve a single feed by its id
    """
    feed = Feed.objects.get(id=request.data['feed_id'])

    return {
        'success': True,
        'message': 'Feed fetched successfully',
        'payload':  feed.__dict__
    }


def get_dynamic_filter(data, request):
    # Display all tags in feeds
    tags = list(
        Feed.objects.annotate(
            name=ArrayAgg('tags__name', distinct=True),
            tag_id=ArrayAgg('tags__id', distinct=True))
        .values('name', 'tag_id').distinct().order_by('name')
    )
    
    return {
        'success': True,
        'message': 'Dynamic filter fetched successfully',
        'payload': tags
    }