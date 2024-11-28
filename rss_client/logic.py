import feedparser
import openai
from django.conf import settings
from accounts.models import User
from sources.models import Source
from .models import Feed, Subscriber, Tag, ProcessedFeed, TagCategory
from rest_framework.validators import ValidationError
from datetime import datetime
from .tasks import summarize_feeds
import json
from django.db.models import Q


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
        {"role": "user", "content": f"the title: {title}, the summary: {summary}"},
        {"role": "user", "content": "the tags should be in following categories:"},
        {"role": "user", "content": "'تصنيف عام', 'أماكن', 'أحداث', 'أشخاص'"},
        {"role": "user", "content": "(اقتصاد, فن, سياسة, أخبار, رياضة, تكنولوجيا, صحة) التصنيف العام يندرج تحته تلك العلامات"},
        {"role": "user", "content": "إليك مثال: عنوان الخبر: الجيش الإسرائيلي ينذر سكان 5 بلدات في جنوب لبنان بإخلائها"},
        {"role": "user", "content": "إليك مثال: ملخص الخبر: أنذر الجيش الإسرائيلي سكان 5 بلدات في جنوب لبنان بإخلائها الفوري تمهيدا لقصفها, زاعما أن نشاطات 'حزب الله' تجبره على العمل بقوة ضده في المناطق التي يتم إنذارها."},
        {"role": "user", "content": "التصنيفات ستكون: الاماكن: جنوب لبنان, التصنيف العام: أخبار, الاحداث: قصف, الاشخاص : الجيش الاسرائيلي, حزب الله"},
        {
            "role": "user",
            "content": "return as a python dict with the keys: 'تصنيف عام', 'أماكن', 'أحداث', 'أشخاص' and the values as lists and dont write format of code"
        },
        {"role": "user", "content": "لا تضع الدول والمدن مثل الولايات المتحده و واشنطن وغيرها ضمن الاشخاص"},
        {
            "role": "user",
            "content": '{"تصنيف عام": ["أخبار"], "أماكن": ["جنوب لبنان"], "أحداث": ["قصف"], "أشخاص": ["الجيش الاسرائيلي", "حزب الله"]}'
        }
    ]


    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=messages
    )
    keywords = response.choices[0].message['content'].strip()
    return keywords


def generate_summary(titles: list, descriptions: list, urls: list):
    messages = [
        {"role": "system", "content": "أنت مساعد مفيد يلخص الأخبار."},
        {"role": "user", "content": "اكتب تقريرًا مرجعيًا يحتوي على عنوان واحد وملخص واحد لجميع العناوين الإخبارية المقدمة أدناه، وقم بتنسيق التقرير ليكون بدون اي / و في شكل tuple:"},
        {"role": "user", "content": "('العنوان', 'الملخص')"},
        {"role": "user", "content": f"العناوين: {titles}، الملخصات: {descriptions}، روابط الأخبار: {urls}"},
    ]

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=messages
    )
    
    return response.choices[0].message['content'].strip()
    

def get_existing_feeds(entries, user_id):
    """Fetch existing feeds to avoid duplicates."""
    existing_feeds = set(
        Feed.objects.filter(
            external_id__in=[entry['id'] for entry in entries],
            user_id=user_id
        ).values_list('external_id', flat=True)
    )
    return existing_feeds


def generate_tags_for_all_entries(entries):
    """Generate tags for each RSS entry."""
    all_tags_data = {
        entry['id']: json.loads(generate_tags_for_feed(entry['title'], entry.get('summary', '')))
        for entry in entries
    }
    return all_tags_data


def fetch_news_from_rss(rss_url: str, limit: int, user_id: int = None):
    feed = feedparser.parse(rss_url)
    entries = feed.entries[:limit]
    
    # Predefined categories
    CATEGORY_NAMES = ["تصنيف عام", "أماكن", "أشخاص", "أحداث"]
    CATEGORY_MAP = {name: TagCategory.objects.get_or_create(name=name)[0] for name in CATEGORY_NAMES}

    # Fetch existing feeds
    existing_feeds = get_existing_feeds(entries, user_id
                                        )
    # Generate tags for all entries
    all_tags_data = generate_tags_for_all_entries(entries)

    all_tag_names = {
        (tag, category)
        for tags_data in all_tags_data.values()
        for category, tags in tags_data.items()
        for tag in tags
    }

    existing_tags = {
        (tag.name, tag.category.name): tag
        for tag in Tag.objects.filter(
            Q(name__in=[name for name, _ in all_tag_names]) &
            Q(category__name__in=[cat for _, cat in all_tag_names])
        ).select_related('category')
    }

    # Prepare tags to create as Tag instances
    tags_to_create = [
        Tag(name=tag_name, category=CATEGORY_MAP[category_name])
        for tag_name, category_name in all_tag_names
        if (tag_name, category_name) not in existing_tags
    ]

    if tags_to_create:
        # Filter out tags already in the database (case-insensitive and unique category match)
        existing_tag_names = Tag.objects.filter(
            Q(name__in=[tag.name for tag in tags_to_create]) &
            Q(category__in=[tag.category for tag in tags_to_create])
        ).values_list('name', 'category')

        # Exclude tags already in the database
        tags_to_create = [
            tag for tag in tags_to_create
            if (tag.name, tag.category) not in existing_tag_names
        ]

    # Bulk create the remaining tags
    if tags_to_create:
        Tag.objects.bulk_create(tags_to_create)

        # Update existing_tags with newly created tags
        new_tags = Tag.objects.filter(
            name__in=[tag.name for tag in tags_to_create],
            category__in=[tag.category for tag in tags_to_create]
        )
        existing_tags.update({
            (tag.name, tag.category.name): tag
            for tag in new_tags
        })

    # Prepare new feeds and tags
    new_feeds = []
    feed_tags = []

    for entry in entries:
        if entry['id'] not in existing_feeds:
            new_feed = Feed(
                external_id=entry['id'],
                title=entry['title'],
                url=entry['link'],
                description=entry.get('summary', ''),
                active=True,
                user_id=user_id,
            )
            new_feeds.append(new_feed)

            # Collect tags for this feed
            entry_tags = [
                existing_tags[(tag, category)]
                for category, tags in all_tags_data[entry['id']].items()
                for tag in tags
            ]
            feed_tags.extend((new_feed, tag) for tag in entry_tags)

    # Bulk create feeds and feed-tag relationships
    if new_feeds:
        Feed.objects.bulk_create(new_feeds)
        Feed.tags.through.objects.bulk_create([
            Feed.tags.through(feed_id=feed.id, tag_id=tag.id)
            for feed, tag in feed_tags
        ])

    return entries


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
    limit = 3
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


def summarize_feeds_by_day(data, request):
    user_id: int = request.user.id
    day_date = datetime.strptime(request.GET.get('day_date', datetime.now().strftime("%Y-%m-%d")), "%Y-%m-%d").date() 

    feeds = Feed.objects.filter(
        user_id=user_id,
        created_at__date=day_date
    )
    
    if not feeds.exists():
        raise ValidationError('No feeds found for this day')
    
    titles: list = list(feeds.values_list('title', flat=True))[:3]
    descriptions: list = list(feeds.values_list('description', flat=True))[:3]
    urls: list = list(feeds.values_list('url', flat=True))[:3]

    processed_feed = ProcessedFeed.objects.filter(
        created_at__date=day_date
    )
    
    if processed_feed.exists():
        return {
            'success': True,
            'message': 'Feeds fetched successfully',
            'payload':  (processed_feed.values())
        }
    
    # Run BG task that summarizes the feeds
    processed_feed = summarize_feeds.delay(titles, descriptions, urls)  
    
    return {
        'success': True,
        'message': 'Feeds fetched successfully',
        'payload':  processed_feed
    }



def subscribe_to_newsletter(data, request):
    """Subscribe to newsletter"""
    email = data.get('email')

    # get the user object
    user = User.objects.filter(email=email).first()

    # check if subscriber already exists
    if Subscriber.objects.filter(user=user).exists():
        # update is_active to true
        Subscriber.objects.filter(user=user).update(is_active=True, subscribed_at=datetime.now())
    else:        
        Subscriber.objects.create(user=user, is_active=True, subscribed_at=datetime.now())
    
    return {
        'success': True,
        'message': 'subscribed successfully',
    }


def unsubscribe_from_newsletter(data, request):
    """Unsubscribe from newsletter"""
    email = data.get('email')

    # get the user object
    user = User.objects.filter(email=email).first()

    # update is_active to false
    Subscriber.objects.filter(user=user).update(is_active=False, unsubscribed_at=datetime.now())
    
    return {
        'success': True,
        'message': 'unsubscribed successfully',
    }
