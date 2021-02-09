# Set the base image to Ubuntu, use a public image
FROM python:3.8.7-buster as builder

COPY . /tmp/antarctic

RUN pip install --no-cache-dir -r /tmp/antarctic/requirements.txt && \
    pip install --no-cache-dir /tmp/antarctic && \
    rm  /tmp/antarctic/requirements.txt

COPY ./antarctic /antarctic/antarctic

# ----------------------------------------------------------------------------------------------------------------------
FROM builder as test

ENV PYTHONPATH "${PYTHONPATH}:/antarctic"

# We install flask here to test some
RUN pip install --no-cache-dir httpretty pytest pytest-cov pytest-html sphinx mongomock requests-mock pytest-notebook && \
    pip install mongomock matplotlib arctic==1.79.4 plotly

WORKDIR /antarctic

#CMD py.test --cov=/antarctic/antarctic  --cov-report html:artifacts/html-coverage --cov-report term --html=artifacts/html-report/report.html test
CMD ["py.test", "--cov=/antarctic/antarctic  --cov-report html:artifacts/html-coverage --cov-report term --html=artifacts/html-report/report.html test"]

# ----------------------------------------------------------------------------------------------------------------------
FROM builder as lint

RUN pip install --no-cache-dir pylint

WORKDIR /antarctic
