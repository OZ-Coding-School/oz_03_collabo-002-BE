#!/bin/sh

set -e

envsubst '${SERVER_NAME}' < /etc/nginx/nginx.conf.template > /etc/nginx/conf.d/default.conf \
>> /etc/nginx/script-reuslt 2>&1

nginx -t >> /etc/nginx/script-reuslt 2>&1

cat /etc/nginx/nginx.conf.template >> /etc/nginx/script-reuslt 2>&1
cat /etc/nginx/conf.d/default.conf >> /etc/nginx/script-reuslt 2>&1

exec nginx -g 'daemon off;' >> /etc/nginx/script-reuslt 2>&1