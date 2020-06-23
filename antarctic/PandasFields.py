import pandas as pd
from mongoengine.base import BaseField
from mongoengine.fields import FileField
from pandas.core.groupby import GroupBy


class SeriesField(BaseField):
    def __set__(self, instance, value):
        # convert the incoming series into a json document
        if value is not None:
            # check it's really a series
            if not isinstance(value, str):
                assert isinstance(value, pd.Series)
                # convert the series into a json string
                value = value.to_json(orient="split")

        # give the (new) value to mum
        super(SeriesField, self).__set__(instance, value)

    def __get__(self, instance, owner):
        # ask mum for the value stored
        x = super(SeriesField, self).__get__(instance, owner)

        if x is not None:
            # convert the value into a series
            return pd.read_json(x, orient="split", typ="series")

        return None


class FrameField(BaseField):
    def __set__(self, instance, value):
        # convert the incoming series into a json document
        if value is not None:
            # check it's really a DataFrame
            if not isinstance(value, str):
                assert isinstance(value, pd.DataFrame)
                # convert the frame into a json string
                value = value.to_json(orient="table")

        # give the (new) value to mum
        super(FrameField, self).__set__(instance, value)

    def __get__(self, instance, owner):
        # ask mum for the value stored
        x = super(FrameField, self).__get__(instance, owner)

        if x is not None:
            return pd.read_json(x, orient="table", typ="frame")

        return None


class OhlcField(FrameField):
    def __set__(self, instance, value):
        if isinstance(value, pd.DataFrame):
            print(value.keys())
            assert {"open", "high", "low", "close", "volume"}.issubset(set(value.keys()))

        super(OhlcField, self).__set__(instance, value)

    def __get__(self, instance, owner):
        x = super(OhlcField, self).__get__(instance, owner)

        if x is not None:
            assert {"open", "high", "low", "close", "volume"}.issubset(set(x.keys()))

        return x

    @classmethod
    def resample(cls, frame, rule):
        d = {"open": lambda x: x.head(1),
             "high": lambda x: x.max(),
             "low": lambda x: x.min(),
             "close": lambda x: x.tail(1),
             "volume": lambda x: x.sum()}

        return pd.DataFrame({name: frame[name].resample(rule, loffset=rule).apply(f) for name, f in d.items()})


class FrameFileField(FileField):
    def __set__(self, instance, value):
        # convert the incoming series into a json document
        if value is not None:
            # check it's really a DataFrame
            assert isinstance(value, pd.DataFrame)
            # convert the frame into a json string
            value = value.to_json(orient="table").encode()

        # give the (new) value to mum
        super(FrameFileField, self).__set__(instance, value)

    def __get__(self, instance, owner):
        # ask mum for the value stored
        x = super(FrameFileField, self).__get__(instance, owner).read().decode()
        return pd.read_json(x, typ="frame", orient="table")
