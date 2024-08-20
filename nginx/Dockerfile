FROM nginx:alpine

COPY nginx.conf.template /etc/nginx/nginx.conf.template

ENV SERVER_NAME=localhost

RUN mkdir -p /vol/web && \
    touch /etc/nginx/conf.d/default.conf && \
    touch /etc/nginx/script-result && \
    chown -R nginx:nginx /vol/web /etc/nginx/conf.d/default.conf

RUN apk add --no-cache gettext

RUN echo '#!/bin/sh' > /docker-entrypoint.sh && \
    echo 'envsubst '\''${SERVER_NAME}'\'' < /etc/nginx/nginx.conf.template > /etc/nginx/conf.d/default.conf' >> /docker-entrypoint.sh && \
    echo 'exec nginx -g "daemon off;"' >> /docker-entrypoint.sh && \
    chmod +x /docker-entrypoint.sh

VOLUME /vol/web

CMD ["/docker-entrypoint.sh"]

