import pandas.testing as pt
import pytest
from mongoengine import Document, connect
from pandas.core.groupby import GroupBy

from antarctic.PandasFields import SeriesField, FrameField, FrameFileField, OhlcField
from test.config import read_pd

from mongomock.gridfs import enable_gridfs_integration
enable_gridfs_integration()

client = connect(db="test", host="mongomock://localhost")


@pytest.fixture
def ts():
    return read_pd("ts.csv", squeeze=True, index_col=0, parse_dates=True)


@pytest.fixture
def prices():
    return read_pd("price.csv", index_col=0, parse_dates=True)


class Symbol(Document):
    close = SeriesField()
    prices = FrameField()
    weights = FrameFileField()
    ohlc = OhlcField()


def test_series(ts):
    s = Symbol()
    s.close = ts
    s.save()
    pt.assert_series_equal(s.close, ts)


def test_series_init(ts):
    s = Symbol(close=ts).save()
    pt.assert_series_equal(s.close, ts)


def test_not_a_series():
    s = Symbol()
    with pytest.raises(AssertionError):
        s.close = 6.0


def test_frame(prices):
    s = Symbol()
    s.prices = prices
    pt.assert_frame_equal(s.prices, prices)


def test_frame_init(prices):
    s = Symbol(prices=prices).save()
    pt.assert_frame_equal(s.prices, prices)


def test_not_a_frame():
    s = Symbol()
    with pytest.raises(AssertionError):
        s.prices = 2.0


def test_frame_series(ts, prices):
    s = Symbol(close=ts, prices=prices)

    pt.assert_frame_equal(s.prices, prices)
    pt.assert_series_equal(s.close, ts)


def test_save(ts, prices):
    s = Symbol(close=ts, prices=prices).save()
    pt.assert_frame_equal(s.prices, prices)
    pt.assert_series_equal(s.close, ts)


def test_fileField(prices):
    s = Symbol()
    s.weights = prices
    pt.assert_frame_equal(s.weights, prices)
    s.save()


def test_fileField_init(prices):
    s = Symbol(weights=prices).save()
    pt.assert_frame_equal(s.weights, prices)


def test_not_a_FileFrame():
    s = Symbol()
    with pytest.raises(AssertionError):
        s.weights = 2.0


def test_ohlc_field():
    s = Symbol()
    ohlc = read_pd("ohlc.csv", index_col="time", parse_dates=True)
    s.ohlc = ohlc
    pt.assert_frame_equal(s.ohlc, ohlc)

    print(s.ohlc.resample(rule="5min").last())
    print(s.ohlc.resample(rule="5min").apply(lambda x: x.tail(1)))
    print(s.ohlc.resample(rule="5min").apply(lambda x: x.head(1)))
    #assert False


    x = OhlcField.resample(frame=s.ohlc, rule="5min")
    pt.assert_frame_equal(x, read_pd("ohlc_resample.csv", index_col="time", parse_dates=True))