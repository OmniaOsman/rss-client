from datetime import datetime
from celery import shared_task
from .models import ProcessedFeed, Feed, Subscriber
import ast
from django.core.mail import EmailMultiAlternatives, send_mail
from django.conf import settings



@shared_task(name='summarize_feeds')
def summarize_feeds(titles, descriptions, urls):
    from rss_client.logic import generate_summary
    print("Hello")
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
    from django.utils.html import strip_tags
    try:
        # Get newsletter content
        summary = ProcessedFeed.objects.filter(created_at__date=datetime.now().date())
        if not summary.exists():
            feeds = Feed.objects.filter(created_at__date=datetime.now().date())
            if feeds.exists():
                title, summary_text = summarize_feeds.delay(
                    list(feeds.values_list('title', flat=True)),
                    list(feeds.values_list('description', flat=True)),
                    list(feeds.values_list('url', flat=True))
                ).get()
            else:
                return
        else:
            title = summary.first().title
            summary_text = summary.first().summary

        # Send to all active subscribers
        subscribers = Subscriber.objects.filter(is_active=True)
        
        for subscriber in subscribers:
            try:
                # Create HTML content
                html_content = f'''
                <html>
                    <head>
                        <meta charset="utf-8">
                    </head>
                    <body dir="rtl" style="font-family: Arial, sans-serif;">
                        <h2>مرحباً {subscriber.name},</h2>
                        <h3>{title}</h3>
                        <div>{summary_text}</div>
                        <p>تحياتي,<br>RSS Client</p>
                    </body>
                </html>
                '''
                
                # Create plain text content
                text_content = strip_tags(html_content)

                # Create email message
                email = EmailMultiAlternatives(
                    subject='Newsletter of the day',
                    body=text_content,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[subscriber.email],
                    headers={'Content-Type': 'text/plain; charset=utf-8'}
                )
                
                # Attach HTML content
                email.attach_alternative(html_content, "text/html")
                
                # Set character encoding
                email.encoding = 'utf-8'
                
                email.send(fail_silently=False)
                
            except Exception as e:
                continue

    except Exception as e:
        raise
