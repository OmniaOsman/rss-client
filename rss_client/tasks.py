from datetime import datetime
from celery import shared_task
from .models import ProcessedFeed, Feed, Subscriber
from django.utils.html import strip_tags
import ast
from django.conf import settings
from django.db.models import Prefetch
from django.core.mail import send_mail
from django.db.models import Prefetch
from reporter.hooks import report_to_publisher

@shared_task
def fetch_news_for_all_subscribers():
    """
    Fetch news for all subscribers by retrieving news from multiple sources.

    This task iterates over all the active subscribers and calls the function
    `get_news_from_multiple_sources` for each subscriber to fetch the latest news
    and updates. This ensures that each subscriber has access to the most recent
    news content from various sources.
    """
    from rss_client.logic import get_news_from_multiple_sources

    # get all the subscribers
    subscribers = Subscriber.objects.all()

    for subscriber in subscribers:
        get_news_from_multiple_sources(data={}, request=subscriber)


@shared_task
def summarize_feeds_by_day():
    """
    Summarize the feeds created today for all active subscribers.

    This task runs once a day and summarizes the feeds created today for all active
    subscribers. It does this by first fetching the feeds created today, then generating
    a summary for each subscriber using the titles and descriptions of the top 3 most
    recent feeds. The summary is then saved as a ProcessedFeed object associated with
    the subscriber's user.

    If a subscriber does not have any feeds associated with them, this task will fetch
    news from multiple sources for the subscriber using the function
    `get_news_from_multiple_sources`.

    After the task is complete, all the feeds created today are made inactive.
    """
    from rss_client.logic import generate_summary, get_news_from_multiple_sources

    day_date = datetime.strptime(datetime.now().strftime("%Y-%m-%d"), "%Y-%m-%d").date()

    # Get the feeds created today
    feeds_queryset = Feed.objects.filter(created_at__date=day_date, active=True)

    # Prefetch active subscribers with their associated users and today's feeds
    subscribers = (
        Subscriber.objects.filter(is_active=True, user__isnull=False)
        .prefetch_related(
            Prefetch("user__feeds", queryset=feeds_queryset, to_attr="todays_feeds")
        )
        .select_related("user")
    )

    for subscriber in subscribers:
        # Use the prefetched feeds
        feeds = subscriber.user.todays_feeds

        if not feeds:
            get_news_from_multiple_sources(data={}, request=subscriber)

        titles = [feed.title for feed in feeds]
        descriptions = [feed.description for feed in feeds]
        urls = [feed.url for feed in feeds]

        # Generate the summary
        result = generate_summary(titles, descriptions, urls)
        print("result", result)

        # Create a ProcessedFeed object for the subscriber's user
        ProcessedFeed.objects.create(
            title=result["title"],
            summary=result["summary"],
            created_at=datetime.now(),
            user=subscriber.user,
        )

        # make feeds inactive
        feeds_queryset.update(active=False)


@shared_task(name="summarize_feeds")
def summarize_feeds(titles, descriptions, urls):
    """
    Summarize a list of feeds.

    This task generates a summary for the given titles, descriptions, and urls of a list of feeds.
    It then creates a ProcessedFeed object with the summary and today's date.

    Args:
        titles (list): A list of titles for the feeds.
        descriptions (list): A list of descriptions for the feeds.
        urls (list): A list of urls for the feeds.

    Returns:
        tuple: A tuple containing the title and summary of the ProcessedFeed object.
    """
    from rss_client.logic import generate_summary

    result = generate_summary(titles, descriptions, urls)

    # Convert the string back to a tuple
    result_tuple = ast.literal_eval(result)

    ProcessedFeed.objects.create(
        title=result_tuple[0],
        summary=result_tuple[1],
        created_at=datetime.now(),
    )

    return result_tuple[0], result_tuple[1]


@shared_task
def send_newsletter():
    try:
        # Get today's date
        today = datetime.now().date()

        # Prefetch ProcessedFeeds for active subscribers
        subscribers = (
            Subscriber.objects.filter(is_active=True, user__isnull=False)
            .select_related("user")
            .prefetch_related(
                Prefetch(
                    "user__processed_feeds",
                    queryset=ProcessedFeed.objects.filter(created_at__date=today),
                    to_attr="todays_summaries",
                )
            )
        )

        for subscriber in subscribers:
            if subscriber.user.email == "first_user@gmail.com":
                continue
            try:
                # Use prefetched summaries
                user_summaries = subscriber.user.todays_summaries

                # Skip if no summaries for this user
                if not user_summaries:
                    print(f"No summaries for user {subscriber.user.email}")
                    continue

                # Get the first summary
                summary = user_summaries[0]
                title = summary.title
                summary_text = summary.summary

                # Create HTML content
                html_content = f"""
                <html>
                    <head>
                        <meta charset="utf-8">
                    </head>
                    <body dir="rtl" style="font-family: Arial, sans-serif;">
                        <h2>مرحباً {subscriber.user.first_name},</h2>
                        <h3>{title}</h3>
                        <div>{summary_text}</div>
                        <p>تحياتي,<br>RSS Client</p>
                    </body>
                </html>
                """

                # Create plain text content
                text_content = strip_tags(html_content)

                # Send the email using Django's send_mail
                send_mail(
                    subject="Newsletter of the day",
                    message=text_content,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[subscriber.user.email],
                    html_message=html_content,
                )

                print(f"Email sent to {subscriber.user.email}")

            except Exception as e:
                print(f"Error sending email to {subscriber.user.email}: {e}")
                continue

    except Exception as e:
        print(f"Error in sending newsletter: {e}")
        raise




@shared_task
def report_summaries():
    try:
        # Get today's date
        today = datetime.now().date()

        # Prefetch ProcessedFeeds for active subscribers
        subscribers = (
            Subscriber.objects.filter(is_active=True, user__isnull=False)
            .select_related("user")
            .prefetch_related(
                Prefetch(
                    "user__processed_feeds",
                    queryset=ProcessedFeed.objects.filter(created_at__date=today),
                    to_attr="todays_summaries",
                )
            )
        )

        for subscriber in subscribers:
       
            try:
                # Use prefetched summaries
                user_summaries = subscriber.user.todays_summaries
                user_publishers = subscriber.user.publishers
                # Skip if no summaries for this user
                if not user_summaries:
                    print(f"No summaries for user {subscriber.user.email}")
                    continue
                if not user_publishers:
                    print(f"No publishers for user {subscriber.user.email}")
                    continue
                
                for summary in user_summaries:
                    for publisher in user_publishers:
                        if report_to_publisher(publisher,summary):
                            print(f"Published summary to {publisher.name} for {subscriber.user.email}")
                        else:
                            print(f"Failed to publish summary to {publisher.name} for {subscriber.user.email}")

            except Exception as e:
                print(f"Error sending email to {subscriber.user.email}: {e}")
                continue

    except Exception as e:
        print(f"Error in sending newsletter: {e}")
        raise
