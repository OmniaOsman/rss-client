from datetime import datetime
from celery import shared_task
from .models import ProcessedFeed, Subscriber
from django.db.models import Prefetch
from .hooks import report_to_publisher

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
