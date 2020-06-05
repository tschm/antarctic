import pandas as pd
from mongoengine.base import BaseField


class SeriesField(BaseField):
    def __set__(self, instance, value):
        if value is not None:
            assert isinstance(value, pd.Series)
            value = value.to_json(orient="split")

        super(SeriesField, self).__set__(instance, value)

    def __get__(self, instance, owner):
        x = super(SeriesField, self).__get__(instance, owner)

        if x is not None:
            return pd.read_json(x, orient="split", typ="series")

        return None


class FrameField(BaseField):
    def __set__(self, instance, value):
        if value is not None:
            assert isinstance(value, pd.DataFrame)
            value = value.to_json(orient="table")

        super(FrameField, self).__set__(instance, value)

    def __get__(self, instance, owner):
        x = super(FrameField, self).__get__(instance, owner)

        if x is not None:
            try:
                return pd.read_json(x, orient="table", typ="frame")
            except:
                return pd.read_json(x, orient="split", typ="frame")

        return None