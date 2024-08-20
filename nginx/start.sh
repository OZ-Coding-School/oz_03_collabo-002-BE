#!/bin/sh

set -e

touch /tmp/script-reuslt

envsubst '${SERVER_NAME}' < /etc/nginx/nginx.conf.template > /etc/nginx/conf.d/default.conf \
>> /tmp/script-reuslt 2>&1

nginx -t >> /tmp/script-reuslt 2>&1

cat /etc/nginx/nginx.conf.template >> /tmp/script-reuslt 2>&1
cat /etc/nginx/conf.d/default.conf >> /tmp/script-reuslt 2>&1

exec nginx -g 'daemon off;' >> /tmp/script-reuslt 2>&1