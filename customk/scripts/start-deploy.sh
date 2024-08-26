#!/bin/sh

python manage.py migrate
python manage.py collectstatic --no-input
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000