import os
from pathlib import Path
from pymongo.errors import ServerSelectionTimeoutError

import pytest
from mongoengine import connect, disconnect


@pytest.fixture(scope="session", name="resource_dir")
def resource_fixture():
    """resource fixture"""
    return Path(__file__).parent / "resources"


@pytest.fixture(scope="function", name="client")
def client_fixture():

    git = os.environ.get("github.ref_name", None)
    #print(git)
    #assert False

    if git:
        x = connect(db="test_pandas", host="mongodb://localhost")
    else:
        x = connect(db="test_pandas", host='mongomock://localhost')

    yield x
    disconnect()
