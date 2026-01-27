"""Provide a custom Polars field type for MongoEngine.

It allows storing polars DataFrames in MongoDB by converting them to and from
parquet-formatted byte streams. This enables efficient storage and retrieval
of polars data structures within MongoDB documents.
"""

from __future__ import annotations

from io import BytesIO
from typing import Any, Literal

import polars as pl
from mongoengine.base import BaseField

CompressionType = Literal["lz4", "uncompressed", "snappy", "gzip", "brotli", "zstd"]


def _read(value: bytes, columns: list[str] | None = None) -> pl.DataFrame:
    """Read a DataFrame from its binary parquet representation.

    Args:
        value: Binary representation of a DataFrame stored as parquet
        columns: Optional list of column names to load (loads all columns if None)

    Returns:
        pl.DataFrame: The reconstructed polars DataFrame

    Examples:
        >>> import polars as pl
        >>> df = pl.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
        >>> data = _write(df)
        >>> result = _read(data)
        >>> result["a"].to_list()
        [1, 2, 3]

        Select specific columns:

        >>> result = _read(data, columns=["b"])
        >>> result.columns
        ['b']

    """
    return pl.read_parquet(BytesIO(value), columns=columns)


def _write(value: pl.DataFrame, compression: CompressionType = "zstd") -> bytes:
    """Convert a Polars DataFrame into a compressed parquet byte-stream.

    The byte-stream encodes in its metadata the structure of the Polars object,
    including column names and data types.

    Args:
        value: The DataFrame to convert
        compression: Compression algorithm to use (default: "zstd")

    Returns:
        bytes: Binary representation of the DataFrame in parquet format

    Examples:
        >>> import polars as pl
        >>> df = pl.DataFrame({"x": [1.0, 2.0], "y": [3.0, 4.0]})
        >>> data = _write(df)
        >>> isinstance(data, bytes)
        True
        >>> data[:4]  # Parquet magic bytes
        b'PAR1'

    """
    buffer = BytesIO()
    value.write_parquet(buffer, compression=compression)
    return buffer.getvalue()


class PolarsField(BaseField):  # type: ignore[misc]
    """Custom MongoEngine field type for storing polars DataFrames.

    This field handles the conversion between polars DataFrames and binary data
    that can be stored in MongoDB. It uses parquet format for efficient storage
    and retrieval of tabular data.
    """

    def __init__(self, compression: CompressionType = "zstd", **kwargs: Any) -> None:
        """Initialize a PolarsField.

        Args:
            compression: Compression algorithm to use for parquet storage (default: "zstd")
            **kwargs: Additional arguments passed to the parent BaseField

        """
        super().__init__(**kwargs)
        self.compression = compression

    def __set__(self, instance: Any, value: pl.DataFrame | bytes | None) -> None:
        """Convert and set the value for this field.

        If the value is a DataFrame, it's converted to a parquet byte stream.
        If it's already bytes, it's stored as-is.

        Args:
            instance: The document instance
            value: The value to set (DataFrame, bytes, or None)

        Raises:
            TypeError: If the value is neither a DataFrame, bytes, nor None

        """
        if value is not None:
            if isinstance(value, pl.DataFrame):
                # Convert DataFrame to binary format for storage
                value = _write(value, compression=self.compression)
            elif isinstance(value, bytes):
                # Already in binary format, store as-is
                pass
            else:
                msg = f"Type of value {type(value)} not supported. Expected DataFrame or bytes."
                raise TypeError(msg)
        super().__set__(instance, value)

    def __get__(self, instance: Any, owner: type) -> pl.DataFrame | PolarsField | None:
        """Retrieve and convert the stored value back to a DataFrame.

        Args:
            instance: The document instance (None for class-level access)
            owner: The document class

        Returns:
            PolarsField: The descriptor itself when accessed at class level
            pl.DataFrame: The retrieved DataFrame when accessed on an instance
            None: If no data is stored

        """
        if instance is None:
            return self

        data = super().__get__(instance, owner)

        if data is not None:
            return _read(data)

        return None
