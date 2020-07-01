import numpy as np
import pandas as pd
import pandas.testing as pt

import pytest
from mongoengine import connect, NotUniqueError
from mongomock.gridfs import enable_gridfs_integration

from antarctic.Document import XDocument
from antarctic.PandasFields import SeriesField
from test.config import resource, read_pd

enable_gridfs_integration()

client = connect(db="test", host="mongomock://localhost")


class Singer(XDocument):
    price = SeriesField()


def test_reference_frame():
    # can't harm to clean a bit
    Singer.objects.delete()

    p1 = Singer(name="Peter")
    p1.reference["A"] = 20.0
    p1.save()

    p2 = Singer(name="Falco")
    p2.reference["A"] = 30.0
    p2.reference["B"] = 10.0
    p2.save()

    frame = Singer.reference_frame(products=[p1, p2])
    assert set(frame.index) == {"Peter", "Falco"}
    assert set(frame.keys()) == {"A", "B"}

    frame = Singer.reference_frame()
    assert set(frame.index) == {"Peter", "Falco"}
    assert set(frame.keys()) == {"A", "B"}


def test_lt():
    assert Singer(name="A") < Singer(name="B")


def test_reference():
    p = Singer(name="Peter Maffay")
    assert p.reference.get("NoNoNo", default=5) == 5

    p.reference["XXX"] = 10
    assert p.reference.keys() == {"XXX"}
    assert {k: v for k, v in p.reference.items()} == {"XXX": 10}


def test_equals():
    # can't harm to clean a bit
    Singer.objects.delete()

    p1 = Singer(name="Peter Maffay")
    p2 = Singer(name="Peter Maffay")

    assert p1 == p2


def test_products():
    # can't harm to clean a bit
    Singer.objects.delete()

    p1 = Singer(name="Peter").save()
    p2 = Singer(name="Falco").save()

    # here we query the database! Hence need the client in the background
    a = Singer.products(names=["Peter"])
    assert len(a) == 1
    assert a[0] == p1

    b = Singer.products()
    assert len(b) == 2
    assert set(b) == {p1, p2}

    frame = Singer.reference_frame(products=[p1, p2])
    assert set(frame.index) == {"Peter", "Falco"}
    assert frame.empty

    frame = Singer.reference_frame()
    assert set(frame.index) == {"Peter", "Falco"}
    assert frame.empty


def test_repr():
    p1 = Singer(name="Peter Maffay")
    assert str(p1) == "<Singer: Peter Maffay>"


def test_not_unique_name():
    # can't harm to clean a bit
    Singer.objects.delete()

    # check that no singer has survived
    s = [singer for singer in Singer.objects]
    assert len(s) == 0

    c1 = Singer(name="AA").save()
    assert c1.name == "AA"

    # try to create a second singer with the same name
    with pytest.raises(NotUniqueError):
        Singer(name="AA").save()


def test_to_dict():
    # can't harm to clean a bit
    Singer.objects.delete()

    c1 = Singer(name="AAA").save()
    c2 = Singer(name="BBB").save()

    assert Singer.to_dict() == {"AAA": c1, "BBB": c2}


def test_apply():
    Singer.objects.delete()
    s1 = Singer(name="Falco").save()
    s2 = Singer(name="Peter Maffay").save()

    s1.price = pd.Series(index=[1, 2, 3], data=[7.0, 9.0, 8.0])
    s2.price = pd.Series(index=[1, 3], data=[8.0, 10.0])
    s3 = Singer(name="Karel Gott").save()
    s1.save()
    s2.save()

    a = pd.Series({name: value for name, value in Singer.apply(f=lambda x: x.price.mean(), default=np.nan)}).dropna()
    pt.assert_series_equal(a, pd.Series({"Falco": 8.0, "Peter Maffay": 9.0}))


def test_repr():
    Singer.objects.delete()
    s1 = Singer(name="Falco").save()
    assert str(s1) == '<Singer: Falco>'
    assert s1.__repr__() == '<Singer: Falco>'


def test_frame():
    Singer.objects.delete()
    s1 = Singer(name="Falco").save()
    s2 = Singer(name="Peter Maffay").save()
    s3 = Singer(name="Karel Gott").save()

    s1.price = pd.Series(index=[1, 2, 3], data=[7.0, 9.0, 8.0])
    s2.price = pd.Series(index=[1, 3], data=[8.0, 10.0])
    s1.save()
    s2.save()

    f = Singer.frame(series="price")
    pt.assert_frame_equal(f, read_pd("frame.csv", index_col=0))

    with pytest.raises(AttributeError):
        Singer.frame(series="wurst")


def test_names():
    Singer.objects.delete()
    s1 = Singer(name="A").save()
    s2 = Singer(name="B").save()
    s3 = Singer(name="C").save()

    assert {s1, s2} == set(Singer.objects(name__in=["A", "B"]).all())
    assert {s2, s1} == set(Singer.objects(name__in=["B", "A"]).all())