FROM jupyter/minimal-notebook:python-3.10.10

USER root

COPY . ${HOME}

RUN chown -R ${NB_UID} ${HOME} && \
    pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-cache --no-interaction -vv

USER ${NB_USER}
