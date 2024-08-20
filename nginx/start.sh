#!/bin/sh

set -e

until nc -z $APP_HOST $APP_PORT; do
    echo "Waiting for the 'app' service..."
    sleep 1
done
echo "SERVER_NAME is set to: ${SERVER_NAME}" >&2

echo "Contents of nginx.conf.template:" >&2
cat /etc/nginx/nginx.conf.template >&2

envsubst '${SERVER_NAME}' < /etc/nginx/nginx.conf.template > /etc/nginx/conf.d/default.conf \
>> /etc/nginx/script-reuslt 2>&1

nginx -t >> /etc/nginx/script-reuslt 2>&1

cat /etc/nginx/nginx.conf.template >> /etc/nginx/script-reuslt 2>&1
cat /etc/nginx/conf.d/default.conf >> /etc/nginx/script-reuslt 2>&1

echo "Starting nginx..." >&2
exec nginx -g 'daemon off;' >> /etc/nginx/script-reuslt 2>&1