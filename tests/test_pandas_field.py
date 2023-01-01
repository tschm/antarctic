from io import BytesIO
from uuid import uuid4

import pandas as pd
import numpy as np

import pandas.testing as pt
import pytest
from mongoengine import Document

from antarctic.pandas_fields import ParquetFrameField, ParquetSeriesField



@pytest.fixture
def ts(resource_dir):
    return pd.read_csv(resource_dir / "ts.csv", squeeze=True, index_col=0, parse_dates=True)


@pytest.fixture
def prices(resource_dir):
    return pd.read_csv(resource_dir / "price.csv", index_col=0, parse_dates=True)


class Symbol(Document):
    close = ParquetSeriesField()
    prices = ParquetFrameField()


def test_series(ts, client):
    s = Symbol()
    s.close = ts
    s.save()
    pt.assert_series_equal(s.close, ts)


def test_series_init(ts, client):
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


def test_frame_init(prices, client):
    s = Symbol(prices=prices).save()
    pt.assert_frame_equal(s.prices, prices)


def test_not_a_frame():
    s = Symbol()
    s.prices = 2.0


def test_frame_series(ts, prices):
    s = Symbol(close=ts, prices=prices)

    pt.assert_frame_equal(s.prices, prices)
    pt.assert_series_equal(s.close, ts)


def test_save(ts, prices, client):
    s = Symbol(close=ts, prices=prices).save()
    pt.assert_frame_equal(s.prices, prices)
    pt.assert_series_equal(s.close, ts)


def test_parquet_file(resource_dir, tmp_path):
    ohlc = pd.read_csv(resource_dir / "ohlc.csv", index_col="time", parse_dates=True)

    with tmp_path / "xxx" as temp:
        ohlc.to_parquet(temp.name, engine='auto', compression=None)
        r = pd.read_parquet(temp.name, engine='auto')

        pt.assert_frame_equal(ohlc, r)


def test_parquet_bytes_io(resource_dir):
    # https://github.com/pandas-dev/pandas/issues/34467
    # This does not work with pandas 1.0.4!
    ohlc = pd.read_csv(resource_dir / "ohlc.csv", index_col="time", parse_dates=True)

    buffer = BytesIO()
    ohlc.to_parquet(buffer, engine='auto', compression=None)

    # don't write buffer to disc
    r = pd.read_parquet(buffer, engine='auto')
    pt.assert_frame_equal(ohlc, r)


def test_parquet_field(resource_dir):
    class Maffay(Document):
        frame = ParquetFrameField(engine="pyarrow", compression="gzip")

    maffay = Maffay()
    ohlc = pd.read_csv(resource_dir / "ohlc.csv", index_col="time", parse_dates=True)
    maffay.frame = ohlc

    pt.assert_frame_equal(maffay.frame, ohlc)


def test_parquet_field_large():
    class Maffay(Document):
        frame = ParquetFrameField(engine="pyarrow", compression=None)

    frame = pd.DataFrame(data=np.random.randn(20000, 500), columns=[str(uuid4()) for _ in range(0, 500)])

    pt.assert_frame_equal(Maffay(frame=frame).frame, frame)


def test_parquet_series_large():
    class Maffay(Document):
        series = ParquetSeriesField(engine="pyarrow", compression=None)

    series = pd.Series(data=np.random.randn(20000,))

    pt.assert_series_equal(Maffay(series=series).series, series)

