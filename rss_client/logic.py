import feedparser
import re
import openai
from django.conf import settings
from accounts.models import User
from sources.models import Source
from .models import Feed, Subscriber, Tag, ProcessedFeed, TagCategory
from rest_framework.exceptions import ValidationError
from datetime import datetime
from .tasks import summarize_feeds
import json
from django.db.models import Q
from xml.etree import ElementTree as ET


tags = []
openai.api_key = settings.OPENAI_API_KEY
domain_name = settings.DOMAIN_NAME


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
        {
            "role": "system",
            "content": "You are a helpful assistant that generates keywords.",
        },
        {
            "role": "user",
            "content": "extract news tags from the following news without any signs or numbers and put a comma between , each tag",
        },
        {"role": "user", "content": f"the title: {title}, the summary: {summary}"},
        {"role": "user", "content": "the tags should be in following categories:"},
        {"role": "user", "content": "'تصنيف عام', 'أماكن', 'أحداث', 'أشخاص'"},
        {
            "role": "user",
            "content": "(اقتصاد, فن, سياسة, أخبار, رياضة, تكنولوجيا, صحة) التصنيف العام يندرج تحته تلك العلامات",
        },
        {
            "role": "user",
            "content": "إليك مثال: عنوان الخبر: الجيش الإسرائيلي ينذر سكان 5 بلدات في جنوب لبنان بإخلائها",
        },
        {
            "role": "user",
            "content": "إليك مثال: ملخص الخبر: أنذر الجيش الإسرائيلي سكان 5 بلدات في جنوب لبنان بإخلائها الفوري تمهيدا لقصفها, زاعما أن نشاطات 'حزب الله' تجبره على العمل بقوة ضده في المناطق التي يتم إنذارها.",
        },
        {
            "role": "user",
            "content": "التصنيفات ستكون: الاماكن: جنوب لبنان, التصنيف العام: أخبار, الاحداث: قصف, الاشخاص : الجيش الاسرائيلي, حزب الله",
        },
        {
            "role": "user",
            "content": "return as a python dict with the keys: 'تصنيف عام', 'أماكن', 'أحداث', 'أشخاص' and the values as lists and dont write format of code",
        },
        {
            "role": "user",
            "content": "لا تضع الدول والمدن مثل الولايات المتحده و واشنطن وغيرها ضمن الاشخاص",
        },
        {
            "role": "user",
            "content": '{"تصنيف عام": ["أخبار"], "أماكن": ["جنوب لبنان"], "أحداث": ["قصف"], "أشخاص": ["الجيش الاسرائيلي", "حزب الله"]}',
        },
    ]

    response = openai.ChatCompletion.create(model="gpt-4o-mini", messages=messages)
    keywords = response.choices[0].message["content"].strip()
    return keywords


def generate_summary(titles, descriptions, urls):
    """
    Generate a response to a given question based on a list of feeds titles and descriptions.

    The function utilizes the OpenAI API to generate a response to a given question based on a
    list of feeds titles and descriptions. The response is in Arabic language.

    Args:
        titles (list): A list of feeds titles.
        descriptions (list): A list of feeds descriptions.
        question (str): The question to be answered.

    Returns:
        str: The generated response.
    """

    context_str = ""
    for i, feed in enumerate(list(zip(titles, descriptions, urls))):
        context_str += f"""
            <source_id> {i+1} </source_id>
            <title> {feed[0]} </title>
            <description> {feed[1]} </description>
            <url> {feed[2]} </url>
            
         """

    messages = [
        {"role": "system", "content": "أنت مساعد مفيد يلخص الأخبار."},
        {
            "role": "user",
            "content": f"""
        ### Task:
        Summerize the provided context, incorporating inline citations in the format [source_id] **only when the <source_id> tag is explicitly provided** in the context.
        
        ### Guidelines:
        - Respond in the same language as the user's query.
        - If the context is unreadable or of poor quality, inform the user and provide the best possible answer.
        - **Only include inline citations using [source_id] when a <source_id> tag is explicitly provided in the context.**  
        - Do not cite if the <source_id> tag is not provided in the context.  
        - Do not use XML tags in your response.
        - Ensure citations are concise and directly related to the information provided.
        
        ### Example of Citation:
        If the user asks about a specific topic and the information is found in "whitepaper.pdf" with a provided <source_id>, the response should include the citation like so:  
        * "According to the study, the proposed method increases efficiency by 20% [whitepaper.pdf]."
        If no <source_id> is present, the response should omit the citation.
        
        ### Output:
        Provide a clear and direct summerization for the provided context, including inline citations in the format [source_id] only when the <source_id> tag is present in the context.
        
        <context>
        {context_str}
        </context>
        """,
        },
        {
            "role": "user",
            "content": "اكتب تقريرًا مرجعيًا يحتوي على عنوان واحد وملخص واحد لجميع العناوين الإخبارية المقدمة",
        },
        {
            "role": "user",
            "content": "result must be json with key 'title' and value 'summary', and put comma and dont write format of code",
        },
    ]

    response = openai.ChatCompletion.create(model="gpt-4o", messages=messages)
    answer = response.choices[0].message["content"].strip()

    # Convert answer to a dictionary using json
    answer = json.loads(answer)

    cleaned_response = answer["summary"].replace("\n", " ").strip()

    numbers = re.findall(r"\[(\d+)\]", cleaned_response)
    numbers = [int(num) for num in numbers]

    if len(numbers) == 0:
        answer["summary"] = cleaned_response
        return answer
    cleaned_response += """

    references:

     """
    for i, n in enumerate(numbers):
        cleaned_response.replace(f"[{n}]", f"[{i+1}]")
        cleaned_response += f"[{i+1}] {urls[n-1]} \n"

    answer["summary"] = cleaned_response

    return answer


def get_existing_feeds(entries, user_id):
    """Fetch existing feeds to avoid duplicates."""
    existing_feeds = set(
        Feed.objects.filter(
            external_id__in=[entry["id"] for entry in entries], user_id=user_id
        ).values_list("external_id", flat=True)
    )
    return existing_feeds


def generate_tags_for_all_entries(entries):
    """Generate tags for each RSS entry."""
    all_tags_data = {
        entry["id"]: json.loads(
            generate_tags_for_feed(entry["title"], entry.get("summary", ""))
        )
        for entry in entries
    }
    return all_tags_data


def fetch_news_from_rss(rss_url: str, limit: int, source_id: int, user_id: int = None):
    """
    Fetches news from an RSS feed and stores them in the database.

    :param rss_url: The URL of the RSS feed
    :param limit: The maximum number of news entries to fetch
    :param user_id: The ID of the user to associate with the news entries
    :return: A list of news entries, without duplicates, and with tags associated
    """
    feed = feedparser.parse(rss_url)
    entries = feed.entries[:limit]

    # Predefined categories
    CATEGORY_NAMES = ["تصنيف عام", "أماكن", "أشخاص", "أحداث"]
    CATEGORY_MAP = {
        name: TagCategory.objects.get_or_create(name=name)[0] for name in CATEGORY_NAMES
    }

    # Fetch existing feeds
    existing_feeds = get_existing_feeds(entries, user_id)

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
            Q(name__in=[name for name, _ in all_tag_names])
            & Q(category__name__in=[cat for _, cat in all_tag_names])
        ).select_related("category")
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
            Q(name__in=[tag.name for tag in tags_to_create])
            & Q(category__in=[tag.category for tag in tags_to_create])
        ).values_list("name", "category")

        # Exclude tags already in the database
        tags_to_create = [
            tag
            for tag in tags_to_create
            if (tag.name, tag.category) not in existing_tag_names
        ]

    # Bulk create the remaining tags
    if tags_to_create:
        Tag.objects.bulk_create(tags_to_create)

        # Update existing_tags with newly created tags
        new_tags = Tag.objects.filter(
            name__in=[tag.name for tag in tags_to_create],
            category__in=[tag.category for tag in tags_to_create],
        )
        existing_tags.update({(tag.name, tag.category.name): tag for tag in new_tags})

    # Prepare new feeds and tags
    new_feeds = []
    feed_tags = []

    for entry in entries:
        if entry["id"] not in existing_feeds:
            new_feed = Feed(
                external_id=entry["id"],
                title=entry["title"],
                url=entry["link"],
                description=entry.get("summary", ""),
                active=True,
                user_id=user_id,
                source_id=source_id,
            )
            new_feeds.append(new_feed)

            # Collect tags for this feed
            entry_tags = [
                existing_tags[(tag, category)]
                for category, tags in all_tags_data[entry["id"]].items()
                for tag in tags
            ]
            feed_tags.extend((new_feed, tag) for tag in entry_tags)

    # Bulk create feeds and feed-tag relationships
    if new_feeds:
        Feed.objects.bulk_create(new_feeds)
        Feed.tags.through.objects.bulk_create(
            [
                Feed.tags.through(feed_id=feed.id, tag_id=tag.id)
                for feed, tag in feed_tags
            ]
        )

    return entries

def get_news_from_sources(user_id):
    # Get sources associated with the user
    sources = Source.objects.filter(user_id=user_id)
    if not sources:
        raise ValidationError("No sources found for this user")

    # Get RSS URLs from the sources
    rss_urls = {}
    for source in sources:
        rss_urls[source.name] = [source.url, source.id]
    all_news = {}
    limit = 25
    for source, value in rss_urls.items():
        news_entries = fetch_news_from_rss(value[0], limit, value[1], user_id)
        all_news[source] = news_entries
    return all_news

def get_news_from_multiple_sources(data, request):
    """
    Fetches news from multiple RSS sources associated with the current user.

    This function takes an empty request body and the current user's ID from the request.
    It fetches all the RSS sources associated with the user, and for each source,
    fetches the latest news entries from the RSS feed using the `fetch_news_from_rss` function.
    It then returns a dictionary with the source name as key and the list of news entries as value.

    Args:
        data (dict): Empty request body.
        request: The HTTP request object containing user information.

    Returns:
        dict: A dictionary containing the success status, a message, and the fetched news entries.
            - 'success' (bool): Indicates if the operation was successful.
            - 'message' (str): A message indicating the result of the operation.
            - 'payload' (dict): A dictionary with the source name as key and the list of news entries as value.
    """
    user_id: int = request.user.id

    # Get sources associated with the user
    all_news = get_news_from_sources(user_id)

    return {
        "success": True,
        "message": "News fetched successfully",
        "payload": all_news,
    }

def get_tags():
    """Retrieve all unique tags collected.

    Returns:
        list: Unique list of tags
    """
    return list(set(tags))


from datetime import datetime
from django.core.exceptions import ValidationError
import xml.etree.ElementTree as ET


def summarize_feeds_by_day(data, request):
    uid = data.get("uid")
    user_id = User.objects.get(uid=uid).id

    # Filter processed feeds for the given date
    processed_feeds = ProcessedFeed.objects.filter(user_id=user_id)

    # Create the RSS XML structure
    rss = ET.Element(
        "rss",
        {
            "version": "2.0",
            "xmlns:content": "http://purl.org/rss/1.0/modules/content/",
            "xmlns:atom": "http://www.w3.org/2005/Atom",
            "xmlns:media": "http://search.yahoo.com/mrss/",
            "xmlns:georss": "http://www.georss.org/georss",
            "xmlns:geo": "http://www.w3.org/2003/01/geo/wgs84_pos#",
        },
    )
    channel = ET.SubElement(rss, "channel")

    # Add metadata to the channel
    ET.SubElement(
        channel,
        "atom:link",
        {
            "href": f"{domain_name}/api/v1/news/summary",
            "rel": "self",
            "type": "application/rss+xml",
        },
    )
    ET.SubElement(channel, "title").text = "Summary of News"
    ET.SubElement(channel, "link").text = f"{domain_name}/api/v1/news/summary"
    ET.SubElement(channel, "managingEditor").text = "support@example.com (Support)"
    ET.SubElement(channel, "webMaster").text = "webmaster@example.com (Webmaster)"
    ET.SubElement(channel, "description").text = "Example Network RSS Feed"
    ET.SubElement(channel, "copyright").text = "© 2024 Example Network"
    ET.SubElement(channel, "lastBuildDate").text = datetime.now().strftime(
        "%a, %d %b %Y %H:%M:%S +0000"
    )
    ET.SubElement(channel, "language").text = "ar"

    # Add feed items from processed_feeds
    for feed in processed_feeds:
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = feed.title
        ET.SubElement(item, "link").text = (
            f"{domain_name}/api/v1/news/summary/{feed.id}"
        )
        ET.SubElement(item, "description").text = f"<![CDATA[{feed.summary}]]>"
        ET.SubElement(item, "pubDate").text = feed.created_at.strftime(
            "%a, %d %b %Y %H:%M:%S +0000"
        )

    # Convert the XML structure to a string
    rss_feed = ET.tostring(rss, encoding="unicode")
    return rss_feed


def subscribe_to_newsletter(data, request):
    """Subscribe to newsletter"""
    user = request.user

    # check if subscriber already exists
    subscribe_obj = Subscriber.objects.filter(user=user)
    if subscribe_obj.exists():
        # update is_active to true
        subscribe_obj.update(is_active=True, subscribed_at=datetime.now())
    else:
        Subscriber.objects.create(
            user=user, is_active=True, subscribed_at=datetime.now()
        )

    return {
        "success": True,
        "message": "subscribed successfully",
    }


def unsubscribe_from_newsletter(data, request):
    """Unsubscribe from newsletter"""
    email = request.user.email

    # get the user object
    user = User.objects.filter(email=email).first()

    # update is_active to false
    Subscriber.objects.filter(user=user).update(
        is_active=False, unsubscribed_at=datetime.now()
    )

    return {
        "success": True,
        "message": "unsubscribed successfully",
    }


def get_summary_by_id(data, request):
    summary_id: int = request.data.get("summary_id")

    # Get the summary object
    summary = ProcessedFeed.objects.filter(id=summary_id).first().summary

    # Return the summary object
    return summary
