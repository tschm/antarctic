import pickle
from io import BytesIO
from bson.binary import Binary

import pandas as pd
from mongoengine.base import BaseField


class SeriesField(BaseField):
    """
    Field for a Pandas Series
    """
    def __set__(self, instance, value):
        # convert the incoming series into a json document
        if value is not None:
            # check it's really a series
            if not isinstance(value, str):
                assert isinstance(value, pd.Series)
                # convert the series into a json string
                value = value.to_json(orient="split")

        # give the (new) value to mum
        super().__set__(instance, value)

    def __get__(self, instance, owner):
        # ask mum for the value stored
        data = super().__get__(instance, owner)

        if data is not None:
            # convert the value into a series
            return pd.read_json(data, orient="split", typ="series")

        return None


class FrameField(BaseField):
    """
    Field for a Pandas DataFrame
    """
    def __set__(self, instance, value):
        # convert the incoming series into a json document
        if isinstance(value, pd.DataFrame):
            value = value.to_json(orient="table")

        # give the (new) value to mum
        super().__set__(instance, value)

    def __get__(self, instance, owner):
        # ask mum for the value stored
        data = super().__get__(instance, owner)

        if data is not None:
            return pd.read_json(data, orient="table", typ="frame")

        return None


class ParquetFrameField(BaseField):
    """
    Field for a Pandas Frame serialized in the parquet format
    """
    def __init__(self, engine="auto", compression=None, **kwargs):
        super().__init__(**kwargs)
        self.engine = engine
        self.compression = compression

    def __set__(self, instance, value):
        # convert the incoming series into a byte-stream document
        if isinstance(value, pd.DataFrame):
            # convert the frame into a json string
            with BytesIO() as buffer:
                value.to_parquet(buffer, engine=self.engine, compression=self.compression)
                value = buffer.getvalue()

        # give the (new) value to mum
        super().__set__(instance, value)

    def __get__(self, instance, owner):
        # ask mum for the value stored
        data = super().__get__(instance, owner)

        if data is not None:
            with BytesIO(data) as buffer:
                return pd.read_parquet(buffer, engine=self.engine)

        return None


class ParquetSeriesField(BaseField):
    """
    Field for a Pandas Series serialized in the parquet format
    """
    def __init__(self, engine="auto", compression=None, **kwargs):
        super().__init__(**kwargs)
        self.engine = engine
        self.compression = compression

    def __set__(self, instance, value):
        # convert the incoming series into a byte-stream document
        if isinstance(value, pd.Series):
            # convert the frame into a json string
            with BytesIO() as buffer:
                value = value.to_frame(name="series")
                value.to_parquet(buffer, engine=self.engine, compression=self.compression)
                value = buffer.getvalue()

        # give the (new) value to mum
        super().__set__(instance, value)

    def __get__(self, instance, owner):
        # ask mum for the value stored
        data = super().__get__(instance, owner)

        if data is not None:
            with BytesIO(data) as buffer:
                series = pd.read_parquet(buffer, engine=self.engine)["series"]
                series.name = None
                return series

        return None


class PicklePandasField(BaseField):
    """
    Field for a Pandas DataFrame pickled
    """
    def __set__(self, instance, value):
        # convert the incoming series into a byte-stream document
        if isinstance(value, (pd.DataFrame, pd.Series)):
            # convert the frame into a bytestream
            value = Binary(pickle.dumps(value))

        # give the (new) value to mum
        super().__set__(instance, value)

    def __get__(self, instance, owner):
        # ask mum for the value stored
        data = super().__get__(instance, owner)

        if data is not None:
            with BytesIO(data) as buffer:
                return pd.read_pickle(buffer, compression=None)

        return None
