import pytest

from antarctic.timeutil import merge
import pandas.testing as pt
import pandas as pd
from test.config import read_pd


@pytest.fixture()
def ts():
    return read_pd("ts.csv", squeeze=True, header=None, parse_dates=True, index_col=0)


def test_merge(ts):
    x = merge(new=ts)
    pt.assert_series_equal(x, ts)

    x = merge(new=ts, old=ts)
    pt.assert_series_equal(x, ts)

    x = merge(new=5 * ts, old=ts)
    pt.assert_series_equal(x, 5 * ts)

    y = merge(None)
    assert not y

    y = merge(pd.Series({}), None)
    pt.assert_series_equal(y, pd.Series({}))

    y = merge(pd.Series({}), pd.Series({}))
    pt.assert_series_equal(y, pd.Series({}))