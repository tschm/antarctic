FROM tschm/jupyter:1.2.0 as builder

# copy everything (as specified by .dockerignore) to /tmp/antarctic
COPY --chown=jovyan:users  . /tmp/antarctic

# and install from there (using setup.py). Also add MongoMock. Cleaning
RUN pip install --no-cache-dir /tmp/antarctic && \
    pip install --no-cache-dir mongomock matplotlib arctic==1.79.4 && \
    rm  -rf /tmp/antarctic

# $WORK is inherited from the tschm/jupyter image
COPY --chown=jovyan:users ./binder/work $WORK

# ----------------------------------------------------------------------------------------------------------------------
FROM builder as test

RUN pip install --no-cache-dir pytest==6.0.1 nbval==0.9.6