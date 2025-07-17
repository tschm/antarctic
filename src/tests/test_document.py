"""
Tests for the XDocument class functionality.

This module contains tests for the XDocument class, which is an extension of
MongoEngine's Document class with additional functionality for working with
collections of documents, extracting reference data, and converting documents
to pandas DataFrames.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pandas.testing as pt
import pytest
from mongoengine import NotUniqueError
from pymongo.mongo_client import MongoClient

from antarctic.document import XDocument
from antarctic.pandas_field import PandasField


class Singer(XDocument):
    """
    Test document class that inherits from XDocument.

    This class is used for testing the functionality of the XDocument class.
    It represents a singer with a price field that stores time series data.
    """

    price = PandasField()


def test_reference_frame(client: MongoClient) -> None:
    """
    Test the reference_frame method of XDocument.

    This test verifies that the reference_frame method correctly extracts
    reference data from documents and creates a properly formatted DataFrame.

    Args:
        client: MongoDB client fixture
    """
    # Clean up any existing Singer documents
    Singer.objects.delete()

    # Create test documents with reference data
    p1 = Singer(name="Peter")
    p1.reference["A"] = 20.0
    p1.save()

    p2 = Singer(name="Falco")
    p2.reference["A"] = 30.0
    p2.reference["B"] = 10.0
    p2.save()

    # Test reference_frame with explicit objects list
    frame = Singer.reference_frame(objects=[p1, p2])
    assert set(frame.index) == {"Peter", "Falco"}
    assert set(frame.keys()) == {"A", "B"}

    # Test reference_frame with default objects (all Singer documents)
    frame = Singer.reference_frame()
    assert set(frame.index) == {"Peter", "Falco"}
    assert set(frame.keys()) == {"A", "B"}


def test_lt() -> None:
    """
    Test the less than comparison operator for XDocument.

    This test verifies that XDocument instances can be compared using the
    less than operator, which compares them by name.
    """
    assert Singer(name="A") < Singer(name="B")


def test_equals(client: MongoClient) -> None:
    """
    Test the equality comparison operator for XDocument.

    This test verifies that two XDocument instances with the same name
    are considered equal, even if they are different instances.

    Args:
        client: MongoDB client fixture
    """
    # Clean up any existing Singer documents
    Singer.objects.delete()

    p1 = Singer(name="Peter Maffay")
    p2 = Singer(name="Peter Maffay")

    assert p1 == p2


def test_products(client: MongoClient) -> None:
    """
    Test the subset method of XDocument.

    This test verifies that the subset method correctly filters documents
    by name and that the reference_frame method works with subsets.

    Args:
        client: MongoDB client fixture
    """
    # Clean up any existing Singer documents
    Singer.objects.delete()

    p1 = Singer(name="Peter").save()
    p2 = Singer(name="Falco").save()

    # Test subset with specific names
    # (requires client fixture for database query)
    a = Singer.subset(names=["Peter"])
    assert len(a) == 1
    assert a[0] == p1

    # Test subset with no names (returns all documents)
    b = Singer.subset()
    assert len(b) == 2
    assert set(b) == {p1, p2}

    # Test reference_frame with explicit objects
    frame = Singer.reference_frame(objects=[p1, p2])
    assert set(frame.index) == {"Peter", "Falco"}
    assert frame.empty

    # Test reference_frame with default objects
    frame = Singer.reference_frame()
    assert set(frame.index) == {"Peter", "Falco"}
    assert frame.empty


def test_not_unique_name(client: MongoClient) -> None:
    """
    Test that document names must be unique.

    This test verifies that attempting to create two documents with the
    same name raises a NotUniqueError.

    Args:
        client: MongoDB client fixture
    """
    # Clean up any existing Singer documents
    Singer.objects.delete()

    # Verify that no Singer documents exist
    s = list(Singer.objects)
    assert len(s) == 0

    # Create a Singer document
    c1 = Singer(name="AA").save()
    assert c1.name == "AA"

    # Attempt to create another Singer with the same name
    with pytest.raises(NotUniqueError):
        Singer(name="AA").save()


def test_to_dict(client: MongoClient) -> None:
    """
    Test the to_dict method of XDocument.

    This test verifies that the to_dict method correctly creates a dictionary
    mapping document names to document objects.

    Args:
        client: MongoDB client fixture
    """
    # Clean up any existing Singer documents
    Singer.objects.delete()

    c1 = Singer(name="AAA").save()
    c2 = Singer(name="BBB").save()

    assert Singer.to_dict() == {"AAA": c1, "BBB": c2}


def test_apply(client: MongoClient) -> None:
    """
    Test the apply method of XDocument.

    This test verifies that the apply method correctly applies a function
    to each document and returns the expected results.

    Args:
        client: MongoDB client fixture
    """
    Singer.objects.delete()
    s1 = Singer(name="Falco").save()
    s2 = Singer(name="Peter Maffay").save()

    # Create test data
    s1.price = pd.Series(index=[1, 2, 3], data=[7.0, 9.0, 8.0]).to_frame(name="price")
    s2.price = pd.Series(index=[1, 3], data=[8.0, 10.0]).to_frame(name="price")

    s1.save()
    s2.save()

    # Apply a function to calculate the mean price for each singer
    a = pd.Series(dict(Singer.apply(func=lambda x: x.price["price"].mean(), default=np.nan))).dropna()

    # Verify the results
    pt.assert_series_equal(a, pd.Series({"Falco": 8.0, "Peter Maffay": 9.0}))


def test_apply_missing(client: MongoClient) -> None:
    """
    Test the apply method with missing data.

    This test verifies that the apply method correctly handles cases where
    some documents are missing the data needed by the applied function.

    Args:
        client: MongoDB client fixture
    """
    Singer.objects.delete()
    s1 = Singer(name="Falco").save()
    s2 = Singer(name="Peter Maffay").save()

    # Only set price data for one singer
    s1.price = pd.Series(index=[1, 2, 3], data=[7.0, 9.0, 8.0]).to_frame(name="price")

    s1.save()
    s2.save()

    # Apply function should use default value for singer with missing data
    a = pd.Series(dict(Singer.apply(func=lambda x: x.price["price"].mean(), default=np.nan)))

    # Verify the results
    pt.assert_series_equal(a, pd.Series({"Falco": 8.0, "Peter Maffay": np.nan}))


def test_repr(client: MongoClient) -> None:
    """
    Test the string representation methods of XDocument.

    This test verifies that the __str__ and __repr__ methods correctly
    format the document's class name and name attribute.

    Args:
        client: MongoDB client fixture
    """
    Singer.objects.delete()
    s1 = Singer(name="Falco").save()
    assert str(s1) == "<Singer: Falco>"
    assert s1.__repr__() == "<Singer: Falco>"


def test_frame(resource_dir: Path, client: MongoClient) -> None:
    """
    Test the frame method of XDocument.

    This test verifies that the frame method correctly extracts a specific
    field and key from multiple documents and creates a properly formatted DataFrame.

    Args:
        resource_dir: Path to the test resources directory
        client: MongoDB client fixture
    """
    Singer.objects.delete()
    s1 = Singer(name="Falco").save()
    s2 = Singer(name="Peter Maffay").save()

    # Create test data
    s1.price = pd.Series(index=[1, 2, 3], data=[7.1, 9.0, 8.0]).to_frame(name="a")
    s2.price = pd.Series(index=[1, 3], data=[8.1, 10.0]).to_frame(name="a")
    s1.save()
    s2.save()

    # Extract data using the frame method
    f = Singer.frame(series="price", key="a")

    # Verify against reference data
    pt.assert_frame_equal(f, pd.read_csv(resource_dir / "frame.csv", index_col=0))

    # Verify that requesting a non-existent field raises an error
    with pytest.raises(AttributeError):
        Singer.frame(series="wurst", key="b")


def test_names(client: MongoClient) -> None:
    """
    Test filtering documents by name.

    This test verifies that documents can be correctly filtered by name
    using the name__in query operator, and that the order of names in the
    query doesn't affect the set of returned documents.

    Args:
        client: MongoDB client fixture
    """
    s1 = Singer(name="A").save()
    s2 = Singer(name="B").save()

    # Order of names in the query shouldn't matter for the set of results
    assert {s1, s2} == set(Singer.objects(name__in=["A", "B"]).all())
    assert {s2, s1} == set(Singer.objects(name__in=["B", "A"]).all())
