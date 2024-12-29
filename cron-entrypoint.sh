#!/bin/bash
celery -A rss_project worker --beat --loglevel=info
# Run the original CMD or any other command you'd like
exec "$@"
