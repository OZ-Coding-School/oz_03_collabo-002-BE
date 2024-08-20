FROM nginx:alpine

COPY nginx.conf.template /etc/nginx/nginx.conf.template

RUN touch /etc/nginx/conf.d/default.conf && \
    touch /etc/nginx/script-result && \
    chown nginx:nginx /etc/nginx/conf.d/default.conf

CMD ["envsubst '${SERVER_NAME}' < /etc/nginx/nginx.conf.template > /etc/nginx/conf.d/default.conf >> /etc/nginx/script-result 2>&1 && exec nginx -g 'daemon off;'"]