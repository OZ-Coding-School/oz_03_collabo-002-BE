FROM nginx:alpine

COPY nginx.conf.template /etc/nginx/nginx.conf.template
COPY start.sh /start.sh

ENV APP_HOST=app
ENV APP_PORT=8000

RUN touch /etc/nginx/conf.d/default.conf && \
    touch /etc/nginx/script-result && \
    chown nginx:nginx /etc/nginx/conf.d/default.conf && \
    chmod +x /start.sh

USER nginx

CMD ["/start.sh"]