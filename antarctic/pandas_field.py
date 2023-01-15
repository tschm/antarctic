"""
This module provides a Pandas type for MongoEngine
"""
from mongoengine.base import BaseField
from typing import List, Optional, Union
from io import BytesIO
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq


def _read(
    value: bytes, columns: Optional[List[str]] = None
) -> Union[pd.DataFrame, pd.Series]:
    """
    Read a binary representation by the write method given below.

    Args:
        value: binary representation as stored in a file

    Returns:
        DataFrame
    """
    with BytesIO(value) as buffer:
        table = pq.read_table(buffer, columns=columns)
        metadata = table.schema.metadata
        frame = table.to_pandas()

        try:
            if metadata[b"antarctic"] == b"Series":
                key = list(frame.keys())[0]
                series = frame[key]
                series.name = key
                return series
        except KeyError:
            return frame

        return frame


def _write(value: Union[pd.DataFrame, pd.Series], compression="zstd") -> bytes:
    """
    Convert a Pandas object into a byte-stream.
    The byte-stream shall encodes in its metadata the nature of the Pandas object.
    """
    if isinstance(value, pd.Series):
        value = value.to_frame(name=value.name)
        table = pa.Table.from_pandas(value)
        metadata = table.schema.with_metadata(
            {**{b"antarctic": b"Series"}, **table.schema.metadata}
        )
    else:
        if not isinstance(value, pd.DataFrame):
            raise AssertionError
        table = pa.Table.from_pandas(value)
        metadata = table.schema.with_metadata(
            {**{b"antarctic": b"Frame"}, **table.schema.metadata}
        )

    table = table.cast(metadata)

    with BytesIO() as buffer:
        pq.write_table(table, buffer, compression=compression)
        return buffer.getvalue()


class PandasField(BaseField):
    """
    Series/Frame type
    """

    def __init__(self, compression="zstd", **kwargs):
        super().__init__(**kwargs)
        self.compression = compression

    def __set__(self, instance, value: Union[pd.DataFrame, pd.Series, None]):
        # convert the incoming series into a byte-stream document
        if isinstance(value, (pd.Series, pd.DataFrame)):
            # give the (new) value to mum
            value = _write(value, compression=self.compression)

        super().__set__(instance, value)

    def __get__(self, instance, owner):
        data = super().__get__(instance, owner)

        if data is not None:
            return _read(data)

        return None
