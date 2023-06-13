# -*- coding: utf-8 -*-
"""global fixtures"""
from __future__ import annotations

from pathlib import Path

import pytest
from mongoengine import connect
from mongoengine import disconnect


@pytest.fixture(scope="session", name="resource_dir")
def resource_fixture():
    """resource fixture"""
    return Path(__file__).parent / "resources"


@pytest.fixture(scope="function", name="client")
def client_fixture():
    """database fixture"""
    db_name = "test"
    with connect(db_name) as connection:
        db = connection.get_database(db_name)
        for collection in db.list_collection_names():
            print(collection)
            print(type(collection))
            col = db[collection]
            col.delete_many({})
    
    yield connect()
    disconnect()
