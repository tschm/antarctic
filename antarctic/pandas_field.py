"""
This module provides a Pandas type for MongoEngine
"""

from __future__ import annotations

from io import BytesIO

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from mongoengine.base import BaseField


def _read(value: bytes, columns: list[str] | None = None) -> pd.DataFrame:
    """
    Read a binary representation by the write method given below.

    Args:
        value: binary representation as stored in a file

    Returns:
        DataFrame
    """
    with BytesIO(value) as buffer:
        table = pq.read_table(buffer, columns=columns)
        return table.to_pandas()


def _write(value: pd.DataFrame, compression="zstd") -> bytes:
    """
    Convert a Pandas DataFrame into a byte-stream.
    The byte-stream shall encodes in its metadata the nature of the Pandas object.
    """
    if isinstance(value, pd.DataFrame):
        table = pa.Table.from_pandas(value)

    with BytesIO() as buffer:
        pq.write_table(table, buffer, compression=compression)
        return buffer.getvalue()


class PandasField(BaseField):
    """
    Series/Frame type
    """

    def __init__(self, compression="zstd", **kwargs):
        """initialize a PandasField"""
        super().__init__(**kwargs)
        self.compression = compression

    def __set__(self, instance, value: pd.DataFrame | bytes):
        """convert the incoming series into a byte-stream document"""
        if value is not None:
            if isinstance(value, pd.DataFrame):
                # give the (new) value to mum
                value = _write(value, compression=self.compression)
            elif isinstance(value, bytes):
                pass
            else:
                raise AssertionError(f"Type of value {type(value)}")
        super().__set__(instance, value)

    def __get__(self, instance, owner):
        """get the pandas object back"""
        data = super().__get__(instance, owner)

        if data is not None:
            return _read(data)

        return None
