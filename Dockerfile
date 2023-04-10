FROM jupyter/minimal-notebook:python-3.10.10

USER root

#FROM python:3.10

# see https://mybinder.readthedocs.io/en/latest/tutorials/dockerfile.html
#ARG NB_USER=jovyan
#ARG NB_UID=1000
#ENV USER ${NB_USER}
#ENV NB_UID ${NB_UID}
#ENV HOME /home/${NB_USER}

#RUN adduser --disabled-password \
#    --gecos "Default user" \
#    --uid ${NB_UID} \
#    ${NB_USER}

# copy everything allowed by .dockerignore
# RUN echo ${HOME}

COPY . ${HOME}

WORKDIR ${HOME}

#RUN pip install --no-cache poetry jupyterlab notebook "jupyter-server<2.0.0" && \
#    poetry config virtualenvs.create false && \
#    poetry install --no-cache --no-interaction -vv && \
#    chown -R ${NB_UID} ${HOME}

RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-cache --no-interaction -vv && \
    chown -R 1000 ${HOME} 

USER jovyan

#ENTRYPOINT []
