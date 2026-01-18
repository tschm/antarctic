"""Provide a custom Pandas field type for MongoEngine.

It allows storing pandas DataFrames in MongoDB by converting them to and from
parquet-formatted byte streams. This enables efficient storage and retrieval
of pandas data structures within MongoDB documents.
"""

from __future__ import annotations

from io import BytesIO
from typing import Any

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from mongoengine.base import BaseField


def _read(value: bytes, columns: list[str] | None = None) -> pd.DataFrame:
    """Read a DataFrame from its binary parquet representation.

    Args:
        value: Binary representation of a DataFrame stored as parquet
        columns: Optional list of column names to load (loads all columns if None)

    Returns:
        pd.DataFrame: The reconstructed pandas DataFrame

    """
    with BytesIO(value) as buffer:
        table = pq.read_table(buffer, columns=columns)
        return table.to_pandas()


def _write(value: pd.DataFrame, compression: str = "zstd") -> bytes:
    """Convert a Pandas DataFrame into a compressed parquet byte-stream.

    The byte-stream encodes in its metadata the structure of the Pandas object,
    including column names, data types, and index information.

    Args:
        value: The DataFrame to convert
        compression: Compression algorithm to use (default: "zstd")

    Returns:
        bytes: Binary representation of the DataFrame in parquet format

    """
    if isinstance(value, pd.DataFrame):
        table = pa.Table.from_pandas(value)

    with BytesIO() as buffer:
        pq.write_table(table, buffer, compression=compression)
        return buffer.getvalue()


class PandasField(BaseField):  # type: ignore[misc]
    """Custom MongoEngine field type for storing pandas DataFrames.

    This field handles the conversion between pandas DataFrames and binary data
    that can be stored in MongoDB. It uses parquet format for efficient storage
    and retrieval of tabular data.
    """

    def __init__(self, compression: str = "zstd", **kwargs: Any) -> None:
        """Initialize a PandasField.

        Args:
            compression: Compression algorithm to use for parquet storage (default: "zstd")
            **kwargs: Additional arguments passed to the parent BaseField

        """
        super().__init__(**kwargs)
        self.compression = compression

    def __set__(self, instance: Any, value: pd.DataFrame | bytes | None) -> None:
        """Convert and set the value for this field.

        If the value is a DataFrame, it's converted to a parquet byte stream.
        If it's already bytes, it's stored as-is.

        Args:
            instance: The document instance
            value: The value to set (DataFrame, bytes, or None)

        Raises:
            AssertionError: If the value is neither a DataFrame, bytes, nor None

        """
        if value is not None:
            if isinstance(value, pd.DataFrame):
                # Convert DataFrame to binary format for storage
                value = _write(value, compression=self.compression)
            elif isinstance(value, bytes):
                # Already in binary format, store as-is
                pass
            else:
                msg = f"Type of value {type(value)} not supported. Expected DataFrame or bytes."
                raise TypeError(msg)
        super().__set__(instance, value)

    def __get__(self, instance: Any, owner: type) -> pd.DataFrame | None:
        """Retrieve and convert the stored value back to a DataFrame.

        Args:
            instance: The document instance
            owner: The document class

        Returns:
            Optional[pd.DataFrame]: The retrieved DataFrame or None if no data

        """
        data = super().__get__(instance, owner)

        if data is not None:
            return _read(data)

        return None
