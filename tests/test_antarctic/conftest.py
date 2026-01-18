"""Global pytest fixtures for the Antarctic test suite.

This module provides fixtures that are available to all test modules in the project.
These fixtures include paths to important directories and a MongoDB client
for database interaction during tests.
"""

from __future__ import annotations

from collections.abc import Generator
from pathlib import Path

import mongomock
import pytest
from mongoengine import connect, disconnect
from pymongo.mongo_client import MongoClient

# @pytest.fixture(scope="session", name="root_dir")
# def root_fixture() -> Path:
#     """Provide the path to the project root directory.
#
#     This fixture returns the absolute path to the root directory of the project,
#     which is useful for accessing files relative to the project root.
#
#     Returns:
#         Path: The absolute path to the project root directory
#
#     """
#     return Path(__file__).parent.parent.parent


@pytest.fixture(scope="session", name="resource_dir")
def resource_fixture() -> Path:
    """Provide the path to the test resources directory.

    This fixture returns the absolute path to the directory containing test
    resources such as sample CSV files and other test data.

    Returns:
        Path: The absolute path to the test resources directory

    """
    return Path(__file__).parent / "resources"


@pytest.fixture(name="client")
def client_fixture() -> Generator[MongoClient, None, None]:
    """Provide a MongoDB client for database operations during tests.

    This fixture creates a MongoDB client using mongomock for testing purposes.
    The client is yielded for the duration of the test function and then disconnected
    when the test is complete. The fixture is function-scoped to ensure a fresh
    connection for each test.

    Returns:
        Generator[MongoClient, None, None]: A MongoDB client for test database operations

    """
    # Ensure any existing connections are closed before creating a new one
    disconnect(alias="default")

    # Use mongomock to create a mock MongoDB client for testing
    yield connect(
        "mongoenginetest",
        host="mongodb://localhost",
        mongo_client_class=mongomock.MongoClient,
        uuidRepresentation="standard",
        alias="default",
    )

    # Ensure the connection is closed after the test is complete
    disconnect(alias="default")
