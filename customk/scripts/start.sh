#!/bin/sh

echo "Waiting for database..."
while ! nc -z db 5432; do
  sleep 0.1
done
echo "Database started"

python manage.py migrate
python manage.py collectstatic --no-input
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000