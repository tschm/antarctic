"""
Tests for the PandasField class functionality.

This module contains tests for the PandasField class, which is a custom MongoEngine
field type for storing pandas DataFrames in MongoDB. The tests verify that the field
correctly handles different types of pandas objects and properly validates input.
"""

from __future__ import annotations

import pandas as pd
import pytest
from mongoengine import Document, StringField
from pymongo.mongo_client import MongoClient

from antarctic.pandas_field import PandasField


class Singer(Document):
    """
    Test document class that uses PandasField.

    This class is used for testing the functionality of the PandasField class.
    It represents a singer with a price field that stores pandas data.
    """

    name = StringField(unique=True, required=True)
    price = PandasField()


def test_write_frame(client: MongoClient) -> None:
    """
    Test storing and retrieving a DataFrame in a PandasField.

    This test verifies that a pandas DataFrame can be stored in a PandasField
    and retrieved with the same structure and data.

    Args:
        client: MongoDB client fixture
    """
    # Create a document with a DataFrame in the PandasField
    s = Singer(name="Maffay1")
    s.price = pd.DataFrame(index=[0, 1], columns=["A", "B"], data=2.0)
    s.save()

    # Verify that the retrieved DataFrame matches the original
    pd.testing.assert_frame_equal(s.price, pd.DataFrame(index=[0, 1], columns=["A", "B"], data=2.0))


def test_write_series(client: MongoClient) -> None:
    """
    Test storing and retrieving a Series in a PandasField.

    This test verifies that a pandas Series (converted to a DataFrame) can be
    stored in a PandasField and retrieved with the same structure and data.

    Args:
        client: MongoDB client fixture
    """
    # Create a document with a Series (converted to DataFrame) in the PandasField
    s = Singer(name="Maffay2")
    s.price = pd.Series(index=[0, 1], data=2.0).to_frame(name="price")
    s.save()

    # Verify that the retrieved Series matches the original
    pd.testing.assert_series_equal(s.price["price"], pd.Series(index=[0, 1], data=2.0, name="price"))


def test_write_series_no_name(client: MongoClient) -> None:
    """
    Test that a Series without a name cannot be stored in a PandasField.

    This test verifies that attempting to store a pandas Series without
    converting it to a DataFrame raises an AssertionError.

    Args:
        client: MongoDB client fixture
    """
    # Create a document
    s = Singer(name="Maffay3")

    # Attempt to store a Series directly (without converting to DataFrame)
    # This should raise an AssertionError
    with pytest.raises(AssertionError):
        s.price = pd.Series(index=[0, 1], data=2.0)
        s.save()


def test_write_non_pandas(client: MongoClient) -> None:
    """
    Test that non-pandas objects cannot be stored in a PandasField.

    This test verifies that attempting to store a non-pandas object
    (like a list) in a PandasField raises an AssertionError.

    Args:
        client: MongoDB client fixture
    """
    # Attempt to store a list in a PandasField
    # This should raise an AssertionError
    with pytest.raises(AssertionError):
        s = Singer(name="Maffay4")
        s.price = [2.0, 2.0]
        s.save()
