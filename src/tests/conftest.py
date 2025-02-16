"""global fixtures"""

from __future__ import annotations

from pathlib import Path

import mongomock
import pytest
from mongoengine import connect, disconnect


@pytest.fixture(scope="session", name="root_dir")
def root_fixture():
    return Path(__file__).parent.parent.parent


@pytest.fixture(scope="session", name="resource_dir")
def resource_fixture():
    """resource fixture"""
    return Path(__file__).parent / "resources"


@pytest.fixture(scope="session", name="client")
def client_fixture():
    """database fixture"""
    # yield connect()
    yield connect(
        "mongoenginetest",
        host="mongodb://localhost",
        mongo_client_class=mongomock.MongoClient,
    )

    disconnect()
