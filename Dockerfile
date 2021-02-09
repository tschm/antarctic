# Set the base image to Ubuntu, use a public image
FROM python:3.8.7-buster as builder

# File Author / Maintainer
MAINTAINER Thomas Schmelzer "thomas.schmelzer@gmail.com"

COPY . /tmp/antarctic

#RUN buildDeps='gcc g++' && \
#    apt-get update && apt-get install -y $buildDeps --no-install-recommends && \
RUN pip install --no-cache-dir -r /tmp/antarctic/requirements.txt && \
    pip install --no-cache-dir mongomock && \
    pip install --no-cache-dir /tmp/antarctic && \
    rm  /tmp/antarctic/requirements.txt
#&& \
#    apt-get purge -y --auto-remove $buildDeps


COPY ./antarctic /antarctic/antarctic

# ----------------------------------------------------------------------------------------------------------------------
FROM builder as test

ENV PYTHONPATH "${PYTHONPATH}:/antarctic"

# We install flask here to test some
RUN pip install --no-cache-dir httpretty pytest pytest-cov pytest-html sphinx mongomock requests-mock pytest-notebook && \
    pip install mongomock matplotlib arctic==1.79.4 plotly

WORKDIR /antarctic

CMD py.test --cov=/antarctic/antarctic  --cov-report html:artifacts/html-coverage --cov-report term --html=artifacts/html-report/report.html test

# ----------------------------------------------------------------------------------------------------------------------
FROM builder as lint

RUN pip install --no-cache-dir pylint

WORKDIR /antarctic

CMD pylint antarctic