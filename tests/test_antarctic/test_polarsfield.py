"""Tests for the PolarsField class functionality.

This module contains tests for the PolarsField class, which is a custom MongoEngine
field type for storing polars DataFrames in MongoDB. The tests verify that the field
correctly handles different types of polars objects and properly validates input.
"""

from __future__ import annotations

import polars as pl
import pytest
from mongoengine import Document, StringField
from polars.testing import assert_frame_equal
from pymongo.mongo_client import MongoClient

from antarctic.polars_field import PolarsField


class Artist(Document):
    """Test document class that uses PolarsField.

    This class is used for testing the functionality of the PolarsField class.
    It represents an artist with a data field that stores polars data.
    """

    name = StringField(unique=True, required=True)
    data = PolarsField()


def test_write_frame(client: MongoClient) -> None:
    """Test storing and retrieving a DataFrame in a PolarsField.

    This test verifies that a polars DataFrame can be stored in a PolarsField
    and retrieved with the same structure and data.

    Args:
        client: MongoDB client fixture

    """
    # Create a document with a DataFrame in the PolarsField
    a = Artist(name="Artist1")
    a.data = pl.DataFrame({"A": [2.0, 2.0], "B": [2.0, 2.0]})
    a.save()

    # Verify that the retrieved DataFrame matches the original
    assert_frame_equal(a.data, pl.DataFrame({"A": [2.0, 2.0], "B": [2.0, 2.0]}))


def test_write_non_polars(client: MongoClient) -> None:
    """Test that non-polars objects cannot be stored in a PolarsField.

    This test verifies that attempting to store a non-polars object
    (like a list) in a PolarsField raises a TypeError.

    Args:
        client: MongoDB client fixture

    """
    # Attempt to store a list in a PolarsField
    # This should raise a TypeError
    a = Artist(name="Artist2")
    with pytest.raises(TypeError):
        a.data = [2.0, 2.0]


def test_write_none(client: MongoClient) -> None:
    """Test that None can be stored in a PolarsField.

    This test verifies that None can be stored and retrieved from a PolarsField.

    Args:
        client: MongoDB client fixture

    """
    # Create a document with None in the PolarsField
    a = Artist(name="Artist3")
    a.data = None
    a.save()

    # Verify that the retrieved value is None
    assert a.data is None
