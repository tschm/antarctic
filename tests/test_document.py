"""testing the document"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pandas.testing as pt
import pytest
from mongoengine import NotUniqueError

from antarctic.document import XDocument
from antarctic.pandas_field import PandasField


class Singer(XDocument):
    """simple document"""

    price = PandasField()


def test_reference_frame(client):
    """test reference data for documents"""
    # can't harm to clean a bit
    Singer.objects.delete()

    p1 = Singer(name="Peter")
    p1.reference["A"] = 20.0
    p1.save()

    p2 = Singer(name="Falco")
    p2.reference["A"] = 30.0
    p2.reference["B"] = 10.0
    p2.save()

    frame = Singer.reference_frame(objects=[p1, p2])
    assert set(frame.index) == {"Peter", "Falco"}
    assert set(frame.keys()) == {"A", "B"}

    frame = Singer.reference_frame()
    assert set(frame.index) == {"Peter", "Falco"}
    assert set(frame.keys()) == {"A", "B"}


def test_lt():
    """test sorting of documents"""
    assert Singer(name="A") < Singer(name="B")


def test_equals(client):
    """test equality"""
    # can't harm to clean a bit
    Singer.objects.delete()

    p1 = Singer(name="Peter Maffay")
    p2 = Singer(name="Peter Maffay")

    assert p1 == p2


def test_products(client):
    """test the subsets of documents"""
    # can't harm to clean a bit
    Singer.objects.delete()

    p1 = Singer(name="Peter").save()
    p2 = Singer(name="Falco").save()

    # here we query the database! Hence need the client in the background
    a = Singer.subset(names=["Peter"])
    assert len(a) == 1
    assert a[0] == p1

    b = Singer.subset()
    assert len(b) == 2
    assert set(b) == {p1, p2}

    frame = Singer.reference_frame(objects=[p1, p2])
    assert set(frame.index) == {"Peter", "Falco"}
    assert frame.empty

    frame = Singer.reference_frame()
    assert set(frame.index) == {"Peter", "Falco"}
    assert frame.empty


def test_not_unique_name(client):
    """trying to create documents of the same type and same name"""
    # can't harm to clean a bit
    Singer.objects.delete()

    # check that no singer has survived
    s = list(Singer.objects)
    assert len(s) == 0

    c1 = Singer(name="AA").save()
    assert c1.name == "AA"

    # try to create a second singer with the same name
    with pytest.raises(NotUniqueError):
        Singer(name="AA").save()


def test_to_dict(client):
    """test create dictionary of documents"""
    # can't harm to clean a bit
    Singer.objects.delete()

    c1 = Singer(name="AAA").save()
    c2 = Singer(name="BBB").save()

    assert Singer.to_dict() == {"AAA": c1, "BBB": c2}


def test_apply(client):
    """apply a function to documents"""
    Singer.objects.delete()
    s1 = Singer(name="Falco").save()
    s2 = Singer(name="Peter Maffay").save()

    s1.price = pd.Series(index=[1, 2, 3], data=[7.0, 9.0, 8.0]).to_frame(name="price")
    s2.price = pd.Series(index=[1, 3], data=[8.0, 10.0]).to_frame(name="price")

    s1.save()
    s2.save()

    a = pd.Series(
        dict(Singer.apply(func=lambda x: x.price["price"].mean(), default=np.nan))
    ).dropna()
    pt.assert_series_equal(a, pd.Series({"Falco": 8.0, "Peter Maffay": 9.0}))


def test_apply_missing(client):
    """data missing"""
    Singer.objects.delete()
    s1 = Singer(name="Falco").save()
    s2 = Singer(name="Peter Maffay").save()

    s1.price = pd.Series(index=[1, 2, 3], data=[7.0, 9.0, 8.0]).to_frame(name="price")

    s1.save()
    s2.save()

    a = pd.Series(
        dict(Singer.apply(func=lambda x: x.price["price"].mean(), default=np.nan))
    )

    pt.assert_series_equal(a, pd.Series({"Falco": 8.0, "Peter Maffay": np.nan}))


def test_repr(client):
    """test repr"""
    Singer.objects.delete()
    s1 = Singer(name="Falco").save()
    assert str(s1) == "<Singer: Falco>"
    assert s1.__repr__() == "<Singer: Falco>"


def test_frame(resource_dir, client):
    """test frame of series data"""
    Singer.objects.delete()
    s1 = Singer(name="Falco").save()
    s2 = Singer(name="Peter Maffay").save()

    s1.price = pd.Series(index=[1, 2, 3], data=[7.1, 9.0, 8.0]).to_frame(name="a")
    s2.price = pd.Series(index=[1, 3], data=[8.1, 10.0]).to_frame(name="a")
    s1.save()
    s2.save()

    f = Singer.frame(series="price", key="a")

    pt.assert_frame_equal(f, pd.read_csv(resource_dir / "frame.csv", index_col=0))

    with pytest.raises(AttributeError):
        Singer.frame(series="wurst", key="b")


def test_names(client):
    """test the names"""
    s1 = Singer(name="A").save()
    s2 = Singer(name="B").save()

    assert {s1, s2} == set(Singer.objects(name__in=["A", "B"]).all())
    assert {s2, s1} == set(Singer.objects(name__in=["B", "A"]).all())
