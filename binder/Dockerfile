FROM tschm/jupyter:1.3.0

# copy everything (as specified by .dockerignore) to /tmp/antarctic
COPY --chown=jovyan:users  . /tmp/antarctic

# and install from there (using setup.py). Also add MongoMock. Cleaning
RUN pip install --no-cache-dir /tmp/antarctic && \
    pip install --no-cache-dir mongomock arctic==1.79.3 && \
    rm  -rf /tmp/antarctic

# $WORK is inherited from the tschm/jupyter image
COPY --chown=jovyan:users ./binder/work $WORK