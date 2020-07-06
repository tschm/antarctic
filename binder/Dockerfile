FROM tschm/jupyter:1.2.0

# File Author / Maintainer
MAINTAINER Thomas Schmelzer "thomas.schmelzer@gmail.com"

# copy everything (as specified by .dockerignore) to /tmp/antarctic
COPY --chown=jovyan:users  . /tmp/antarctic

# and install from there (using setup.py). Also add MongoMock. Cleaning
RUN pip install --no-cache-dir /tmp/antarctic && \
    pip install --no-cache-dir mongomock && \
    rm  -rf /tmp/antarctic

# $WORK is inherited from the tschm/jupyter image
COPY --chown=jovyan:users ./binder/work $WORK