FROM python:3.12-alpine3.20

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt
COPY ./customk /app

WORKDIR /app
EXPOSE 8000

ARG DEV=true

RUN apk add --update --no-cache libffi-dev
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    if [ $DEV = "true" ]; \
        then /py/bin/pip install -r /tmp/requirements.dev.txt ; \
    else \
        /py/bin/pip install -r /tmp/requirements.txt ; \
    fi && \
    rm -rf /tmp && \
    adduser \
        --disabled-password \
        --no-create-home \
        django-user
ENV PATH="/py/bin:$PATH"

USER django-user
