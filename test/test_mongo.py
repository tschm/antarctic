import pandas as pd
import pandas.util.testing as pdt
import pytest

from antarctic.mongo import create_collection


@pytest.fixture()
def ts1():
    return pd.Series(data=[100, 200], index=[0, 1]).to_frame(name="a")


@pytest.fixture()
def ts2():
    return pd.Series(data=[300, 300], index=[1, 2]).to_frame(name="b")


@pytest.fixture()
def col(ts1):
    collection = create_collection()
    # Note that we don't define a name here...
    collection.upsert(value=ts1, key="PX_LAST", First="Hans", Last="Dampf")
    collection.upsert(value=ts1, key="PX_LAST", First="Hans", Last="Maffay")
    collection.upsert(value=ts1, key="PX_OPEN", First="Hans", Last="Maffay")
    collection.upsert(value=2.0, key="XXX", name="HANS")
    collection.upsert(value=3.0, key="XXX", name="PETER")
    return collection


class TestMongo(object):
    def test_find_one(self, col):
        assert col.find_one(name="HANS").data == 2.0
        assert col.find_one(name="HANS").meta == {"key": "XXX", "name": "HANS"}
        assert col.find_one(name="HANS").t

    def test_not_unique(self, col):
        # not unique
        with pytest.raises(AssertionError):
            # there are three Hans
            col.find_one(First="Hans")

    def test_no_find(self, col):
        # there is no Peter
        assert col.find_one(First="Peter") is None

    def test_assert_insert(self, col, ts1):
        # can not upsert Hans are there are two of them...
        with pytest.raises(AssertionError):
            col.upsert(value=ts1, key="PX_LAST", First="Hans")

        # check that there are indeed 3
        assert len([x for x in col.find(First="Hans")]) == 3

    def test_overwrite(self, col, ts2):
        col.upsert(value=ts2, key="PX_LAST", First="Hans", Last="Maffay")
        pdt.assert_frame_equal(ts2, col.find_one(Last="Maffay", key="PX_LAST").data)

    def test_repr(self, col):
        assert str(col)
        assert col.name

    #def test_read_write_merge_last(self, col, ts2):
    #    col.write(data=ts2, key="PX_OPEN", name="H")
    #    col.merge(data=ts2.tail(10), key="PX_OPEN", name="H")
    #    pdt.assert_series_equal(col.read(key="PX_OPEN", name="H"), ts2)
    #    assert col.last(key="PX_OPEN", name="H") == ts2.last_valid_index()

    def test_ts(self, col):
        for a in col.find(First="Hans", Last="Maffay"):
            assert a.meta["First"] == "Hans"
            assert a.meta["Last"] == "Maffay"
            assert a.meta["key"] in {"PX_LAST", "PX_OPEN"}

