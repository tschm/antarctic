import pandas.testing as pt
import pytest
from mongoengine import Document, connect

from antarctic.PandasFields import SeriesField, FrameField
from test.config import read_pd

client = connect(db="test", host="mongomock://localhost")


class Singer(Document):
    close = SeriesField()
    prices = FrameField()


def test_series():
    s = Singer()
    ts = read_pd("ts.csv", squeeze=True, index_col=0, parse_dates=True)
    s.close = ts
    pt.assert_series_equal(s.close, ts)

    s = Singer(close=ts)
    pt.assert_series_equal(s.close, ts)

    with pytest.raises(AssertionError):
        s.close = 6.0


def test_frame():
    s = Singer()
    frame = read_pd("price.csv", index_col=0, parse_dates=True)
    s.prices = frame
    pt.assert_frame_equal(s.prices, frame)

    s = Singer(prices=frame)
    pt.assert_frame_equal(s.prices, frame)

    with pytest.raises(AssertionError):
        s.prices = 2.0


def test_frame_series():
    frame = read_pd("price.csv", index_col=0, parse_dates=True)
    ts = read_pd("ts.csv", squeeze=True, index_col=0, parse_dates=True)
    s = Singer(close=ts, prices=frame)

    pt.assert_frame_equal(s.prices, frame)
    pt.assert_series_equal(s.close, ts)