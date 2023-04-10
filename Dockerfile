FROM jupyter/minimal-notebook:dbd4f919476a

USER root

COPY . ${HOME}

RUN chown -R ${NB_UID} ${HOME} && \
    pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-cache --no-interaction -vv

USER ${NB_USER}
