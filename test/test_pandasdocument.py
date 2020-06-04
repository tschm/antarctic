import pandas as pd
import pandas.testing as pdt
import pytest
from mongoengine import connect

from antarctic.pandasdocument import PandasDocument, NotUniqueError
from antarctic.timeutil import merge
from test.config import read_pd

client = connect(db="test", host="mongomock://localhost")


class Singer(PandasDocument):
    pass


class TestEngine(object):
    def test_document(self):
        # Create a new page and add tags
        p = Singer(name="Peter Maffay")
        assert p.name == "Peter Maffay"

    def test_lt(self):
        assert Singer(name="A") < Singer(name="B")

    def test_reference(self):
        p = Singer(name="Peter Maffay")
        assert p.reference.get("NoNoNo", default=5) == 5

        p.reference["XXX"] = 10
        assert p.reference.keys() == {"XXX"}
        assert {k: v for k, v in p.reference.items()} == {"XXX": 10}

    def test_equals(self):
        # can't harm to clean a bit
        Singer.objects.delete()

        p1 = Singer(name="Peter Maffay")
        p2 = Singer(name="Peter Maffay")

        assert p1 == p2

    def test_merge(self):
        # can't harm to clean a bit
        Singer.objects.delete()

        p = Singer(name="Peter Maffay")

        ts1 = pd.Series(index=[1, 2], data=[3.3, 4.3])
        ts2 = pd.Series(index=[2, 3], data=[5.3, 6.3])

        p.close = ts1
        p.close = merge(old=p.close, new=ts2)

        pdt.assert_series_equal(p.close, pd.Series(index=[1, 2, 3], data=[3.3, 5.3, 6.3]))

    def test_products(self):
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

    def test_reference_frame(self):
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

    def test_ts(self):
        # can't harm to clean a bit
        Singer.objects.delete()

        p1 = Singer(name="Peter Maffay")
        p1.price = pd.Series(data=[2, 3, 5], index=[pd.Timestamp("2010-01-01"), pd.Timestamp("2010-01-03"), pd.Timestamp("2010-01-05")])
        p1.save()

        p2 = Singer(name="Falco").save()
        assert p1.reference == {}

        frame = Singer.pandas_frame(item="price", products=[p1, p2])
        assert set(frame.keys()) == {"Peter Maffay"}
        pdt.assert_series_equal(p1.price, frame["Peter Maffay"], check_names=False)

        frame = Singer.pandas_frame(item="price")
        assert set(frame.keys()) == {"Peter Maffay"}
        pdt.assert_series_equal(p1.price, frame["Peter Maffay"], check_names=False)

    def test_pandas_wrong(self):
        # can't harm to clean a bit
        Singer.objects.delete()

        p1 = Singer(name="Peter Maffay")
        p1.price = 5.0
        assert Singer.pandas_frame(item="price", products=[p1]).empty

    def test_repr(self):
        p1 = Singer(name="Peter Maffay")
        assert str(p1) == "<Singer: Peter Maffay>"

    def test_not_unique_name(self):
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

    def test_to_dict(self):
        # can't harm to clean a bit
        Singer.objects.delete()

        c1 = Singer(name="AAA").save()
        c2 = Singer(name="BBB").save()

        assert Singer.to_dict() == {"AAA": c1, "BBB": c2}

    def test_frame(self):
        frame = read_pd("reference.csv", index_col=[0,1])
        s = Singer(name="Peter Maffay")
        s.frame = frame
        pdt.assert_frame_equal(frame, s.frame)

    def test_frame_timeseries(self):
        frame = read_pd("price.csv", index_col=0)
        s = Singer(name="Peter Maffay")
        s.frame = frame
        pdt.assert_frame_equal(frame, s.frame)