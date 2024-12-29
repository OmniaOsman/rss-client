#!/bin/bash
python manage.py makemigrations
# Apply database migrations (uncomment if needed)
python manage.py migrate
# load data from data seed file to database
python3 manage.py loaddata 0001_category.json
# Run the original CMD or any other command you'd like
python manage.py runserver 0.0.0.0:8000
exec "$@"
