FROM python:3.9-slim-buster

RUN apt-get -y update && \
    apt-get -y upgrade

ENV APP_NAME=app
COPY requirements.txt /tmp
RUN pip install -r /tmp/requirements.txt

RUN mkdir -p /$APP_NAME
COPY src/ /$APP_NAME/src
COPY tests /$APP_NAME/tests

WORKDIR /$APP_NAME

ENV PYTHONPATH=$PYTHONPATH:/$APP_NAME/src

CMD uvicorn entrypoints.api:app --host 0.0.0.0 --reload
