FROM nginx:alpine

ARG SERVER_NAME
ENV SERVER_NAME=${SERVER_NAME}

COPY nginx.conf.template /etc/nginx/nginx.conf.template
RUN envsubst '$SERVER_NAME' < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf