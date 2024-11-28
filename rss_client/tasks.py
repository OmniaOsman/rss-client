from datetime import datetime
from celery import shared_task
from .models import ProcessedFeed, Feed, Subscriber
from django.utils.html import strip_tags
import ast
from django.conf import settings
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from django.db.models import Prefetch


@shared_task
def fetch_news_for_all_subscribers():
    from rss_client.logic import get_news_from_multiple_sources
    # get all the subscribers
    subscribers = Subscriber.objects.all()

    for subscriber in subscribers:
        get_news_from_multiple_sources(data={}, request=subscriber)


@shared_task
def summarize_feeds_by_day():
    from rss_client.logic import generate_summary, get_news_from_multiple_sources
    day_date = datetime.strptime(datetime.now().strftime("%Y-%m-%d"), "%Y-%m-%d").date() 

    # Get the feeds created today
    feeds_queryset = Feed.objects.filter(created_at__date=day_date)

    # Prefetch active subscribers with their associated users and today's feeds
    subscribers = Subscriber.objects.filter(
        is_active=True, 
        user__isnull=False
    ).prefetch_related(
        Prefetch('user__feeds', 
                 queryset=feeds_queryset, 
                 to_attr='todays_feeds')
    ).select_related('user')

    for subscriber in subscribers:
        try:
            # Use the prefetched feeds
            feeds = subscriber.user.todays_feeds

            if not feeds:
                get_news_from_multiple_sources(data={}, request=subscriber)

            titles = [feed.title for feed in feeds[:3]]
            descriptions = [feed.description for feed in feeds[:3]]
            urls = [feed.url for feed in feeds[:3]]

            # Generate the summary
            result = generate_summary(titles, descriptions, urls)
            
            # Convert the string back to a tuple
            result_tuple = ast.literal_eval(result)
            print("result_tuple", result_tuple)

            # Create a ProcessedFeed object for the subscriber's user
            ProcessedFeed.objects.create(
                title=result_tuple[0],
                summary=result_tuple[1],
                created_at=datetime.now(),
                user=subscriber.user
            )
        
        except Exception as e:
            print(f"Error processing subscriber {subscriber.id}: {e}")


@shared_task(name='summarize_feeds')
def summarize_feeds(titles, descriptions, urls):
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
        subscribers = Subscriber.objects.filter(
            is_active=True, 
            user__isnull=False
        ).select_related('user').prefetch_related(
            Prefetch('user__processed_feeds', 
                     queryset=ProcessedFeed.objects.filter(created_at__date=today),
                     to_attr='todays_summaries')
        )

        # Initialize SendGrid client
        sg = SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)

        for subscriber in subscribers:
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
                html_content = f'''
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
                '''
                
                # Create plain text content
                text_content = strip_tags(html_content)

                # Create email message
                from_email = Email(settings.DEFAULT_FROM_EMAIL)
                to_email = To(subscriber.user.email)
                subject = 'Newsletter of the day'
                content = Content("text/plain", text_content)

                # Create Mail object
                mail = Mail(from_email, to_email, subject, content)
                mail.add_content(Content("text/html", html_content))

                # Send email via SendGrid
                response = sg.client.mail.send.post(request_body=mail.get())
                
                print(f"Email sent to {subscriber.user.email}, status: {response.status_code}")

            except Exception as e:
                print(f"Error sending email to {subscriber.user.email}: {e}")
                continue

    except Exception as e:
        print(f"Error in sending newsletter: {e}")
        raise

