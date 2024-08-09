FROM python:3.12-alpine3.19

# LABEL maintainer="gomnonix"

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /tmp/requirements.txt
COPY ./customk /app

WORKDIR /app
EXPOSE 8000

ARG DEV=false

RUN apk add --update --no-cache libffi-dev
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    rm -rf /tmp


ENV PATH="/py/bin:$PATH"
