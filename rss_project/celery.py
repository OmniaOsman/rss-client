from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.signals import task_failure
from django.conf import settings
# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rss_project.settings')

app = Celery('rss_project')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()
app.autodiscover_tasks(['rss_client'])

# Using Redis as the result backend.
app.conf.broker_url = settings.CELERY_BROKER_URL
app.conf.result_backend = settings.CELERY_BROKER_URL
app.conf.update(
    beat_log_level="DEBUG"
)
app.conf.enable_utc = False
app.conf.timezone = 'Africa/Cairo'


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
    
