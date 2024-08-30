#!/bin/sh

echo "Waiting for database..."
while ! nc -z localdb 5432; do
  sleep 0.1
done
echo "Database started"

python manage.py migrate
python manage.py collectstatic --no-input

exec gunicorn config.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 5 \
  --access-logfile logs/app_access.log \
  --error-logfile logs/app_error.log \
  --timeout 30