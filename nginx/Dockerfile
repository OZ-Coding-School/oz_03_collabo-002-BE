FROM nginx:alpine

COPY nginx.conf.template /etc/nginx/nginx.conf.template
COPY start.sh /start.sh

RUN touch /etc/nginx/conf.d/default.conf && \
    touch /etc/nginx/script-result && \
    chmod +x /start.sh

CMD ["/start.sh"]