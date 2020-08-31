# Set the base image to Ubuntu, use a public image
FROM python:3.7.7-slim-stretch as builder

COPY . /tmp/antarctic

#RUN buildDeps='g++=4:6.3.0-4' && \
RUN apt-get update && \
    apt-get install -y  'g++=4:6.3.0-4' --no-install-recommends && \
    pip install --no-cache-dir -r /tmp/antarctic/requirements.txt && \
    pip install --no-cache-dir /tmp/antarctic && \
    rm  /tmp/antarctic/requirements.txt && \
    apt-get purge -y --auto-remove "g++" && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY ./antarctic /antarctic/antarctic

#### Here the test-configuration
FROM builder as test

COPY ./test /antarctic/test

RUN pip install --no-cache-dir -r /antarctic/test/requirements.txt
