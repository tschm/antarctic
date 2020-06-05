import pandas as pd
from mongoengine.base import BaseField


class SeriesField(BaseField):
    def __set__(self, instance, value):
        # convert the incoming series into a json document
        if value is not None:
            # check it's really a series
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
            assert isinstance(value, pd.DataFrame)
            # convert the frame into a json string
            value = value.to_json(orient="table")

        # give the (new) value to mum
        super(FrameField, self).__set__(instance, value)

    def __get__(self, instance, owner):
        # ask mum for the value stored
        x = super(FrameField, self).__get__(instance, owner)

        if x is not None:
            # convert the json string back into a DataFrame
            try:
                # This is some historic baggage as I have still some DataFrames stored in the split format
                return pd.read_json(x, orient="table", typ="frame")
            except:
                return pd.read_json(x, orient="split", typ="frame")

        return None