import pandas as pd
from mongoengine.base import BaseField


class PandasField(BaseField):
    def __init__(self, **kwargs):
        super(PandasField, self).__init__(**kwargs)

    def __set__(self, instance, value):
        if value is not None:
            value = self.to_python(value)
        super(PandasField, self).__set__(instance, value)

    def __get__(self, instance, owner):
        x = super(PandasField, self).__get__(instance, owner)
        if x is not None:
            x = self.to_mongo(x)

        return x


class SeriesField(PandasField):
    def to_python(self, value):
        if isinstance(value, str):
            return value
        assert isinstance(value, pd.Series), "The type is {}".format(type(value))
        return value.to_json(orient="split")

    def to_mongo(self, value):
        return pd.read_json(value, orient="split", typ="series")


class FrameField(PandasField):
    def to_python(self, value):
        if isinstance(value, str):
            return value
        assert isinstance(value, pd.DataFrame), "The type is {}".format(type(value))
        return value.to_json(orient="table")

    def to_mongo(self, value):
        return pd.read_json(value, orient="table", typ="frame")
