FROM nginx:alpine

COPY nginx.conf.template /etc/nginx/nginx.conf.template
COPY start.sh /start.sh

RUN touch /etc/nginx/conf.d/default.conf && \
    chown nginx:nginx /etc/nginx/conf.d/default.conf && \
    chmod +x /start.sh

USER nginx

CMD ["/start.sh"]