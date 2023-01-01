FROM jupyter/scipy-notebook:aec555e49be6 as builder

# copy everything (as specified by .dockerignore) to /tmp/antarctic
COPY --chown=jovyan:users  . /tmp/antarctic

# and install from there (using setup.py). Also add MongoMock. Cleaning
RUN pip3 install --user --no-cache-dir /tmp/antarctic && \
    pip3 install --user --no-cache-dir \
        mongomock \
        arctic==1.79.4 \
    && rm  -rf /tmp/antarctic

# $WORK is inherited from the tschm/jupyter image
COPY --chown=jovyan:users ./binder/work $WORK
