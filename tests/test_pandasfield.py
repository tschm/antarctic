"""testing the document"""

import pandas as pd
import pytest
from mongoengine import Document, StringField

from antarctic.pandas_field import PandasField


class Singer(Document):
    """simple document"""
    name = StringField(unique=True, required=True)
    price = PandasField()


def test_write_frame(client):
    s = Singer(name="Maffay")
    s.price = pd.DataFrame(index=[0,1], columns=["A","B"], data=2.0)
    s.save()

    pd.testing.assert_frame_equal(s.price, pd.DataFrame(index=[0,1], columns=["A","B"], data=2.0))


def test_write_series(client):
    s = Singer(name="Maffay")
    s.price = pd.Series(index=[0,1], data=2.0).to_frame(name="price")
    s.save()

    pd.testing.assert_series_equal(s.price["price"], pd.Series(index=[0, 1], data=2.0, name="price"))

def test_write_series_no_name(client):
    s = Singer(name="Maffay")
    with pytest.raises(AssertionError):
        s.price = pd.Series(index=[0,1], data=2.0)
        s.save()


def test_write_non_pandas(client):
    with pytest.raises(AssertionError):
        s = Singer(name="Maffay")
        s.price = [2.0, 2.0]
        s.save()