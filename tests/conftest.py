import os
from pathlib import Path

import pytest
from mongoengine import connect, disconnect
from pymongo.errors import ServerSelectionTimeoutError


@pytest.fixture(scope="session", name="resource_dir")
def resource_fixture():
    """resource fixture"""
    return Path(__file__).parent / "resources"


@pytest.fixture(scope="function", name="client")
def client_fixture():

    git = os.environ.get("github.ref_name")

    if git:
        x = connect(db="test_pandas", host="mongodb://localhost")
    else:
        x = connect(db="test_pandas", host="mongomock://localhost")

    yield x

    disconnect()
