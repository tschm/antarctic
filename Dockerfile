# Set the base image to Ubuntu, use a public image
FROM python:3.7.7-slim-stretch as builder

COPY . /tmp/antarctic

RUN buildDeps='gcc g++' && \
    apt-get update && apt-get install -y $buildDeps --no-install-recommends && \
    pip install --no-cache-dir -r /tmp/antarctic/requirements.txt && \
    pip install --no-cache-dir mongomock && \
    pip install --no-cache-dir /tmp/antarctic && \
    rm  /tmp/antarctic/requirements.txt && \
    apt-get purge -y --auto-remove $buildDeps


COPY ./antarctic /antarctic/antarctic

#### Here the test-configuration
FROM builder as test

# We install flask here to test some
RUN pip install --no-cache-dir httpretty pytest pytest-cov pytest-html sphinx mongomock requests-mock pytest-notebook && \
    pip install mongomock matplotlib arctic==1.79.3 plotly

WORKDIR /antarctic

CMD py.test --cov=/antarctic/antarctic  --cov-report html:artifacts/html-coverage --cov-report term --html=artifacts/html-report/report.html test