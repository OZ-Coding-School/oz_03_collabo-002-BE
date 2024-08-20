#!/bin/sh

set -e

envsubst '${SERVER_NAME}' < /etc/nginx/nginx.conf.template > /etc/nginx/conf.d/default.conf

nginx -t

exec nginx -g 'daemon off;'