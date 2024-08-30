#!/bin/sh

python manage.py migrate
python manage.py collectstatic --no-input

exec gunicorn config.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 5 \
  --access-logfile logs/gunicorn_access.log \
  --error-logfile logs/gunicorn_error.log \
  --timeout 30