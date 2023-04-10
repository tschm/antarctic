FROM python:3.10-slim

# see https://mybinder.readthedocs.io/en/latest/tutorials/dockerfile.html
ARG NB_USER=jovyan
ARG NB_UID=1000
ENV USER ${NB_USER}
ENV NB_UID ${NB_UID}
ENV HOME /home/${NB_USER}

RUN adduser --disabled-password \
    --gecos "Default user" \
    --uid ${NB_UID} \
    ${NB_USER}

# copy everything allowed by .dockerignore
COPY . ${HOME}

WORKDIR ${HOME}

RUN pip install --no-cache poetry jupyterlab notebook && \
    chown -R ${NB_UID} ${HOME} && \
    poetry config virtualenvs.create false && \
    poetry install --no-cache --no-interaction -vv

USER ${NB_USER}

ENTRYPOINT []