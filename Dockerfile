FROM jupyter/base-notebook

USER root

COPY . ${HOME}

RUN chown -R ${NB_UID} ${HOME} && \
    pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-cache --no-interaction -vv

USER ${NB_USER}
