"""Extension of the MongoEngine Document class with additional functionality.

This module provides an abstract base class that extends MongoEngine's Document
with additional methods for working with collections of documents, extracting
reference data, and converting documents to pandas DataFrames.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator
from datetime import UTC, datetime
from typing import Any

import pandas as pd
from bson.json_util import RELAXED_JSON_OPTIONS
from mongoengine import DateTimeField, DictField, Document, QuerySet, StringField


class XDocument(Document):
    """Abstract base class for MongoDB documents with extended functionality.

    XDocument is an abstract MongoDB Document that cannot be instantiated directly.
    All concrete objects such as Symbols or Strategies should inherit from this class.
    It provides common functionality for working with collections of documents,
    extracting reference data, and converting documents to pandas DataFrames.

    Attributes:
        name: Unique identifier for the document
        reference: Dictionary for storing reference data
        date_modified: Timestamp of the last modification

    """

    meta = {"abstract": True}

    name = StringField(unique=True, required=True)
    reference = DictField()

    # Date modified - automatically updated when the document is saved
    date_modified = DateTimeField(default=lambda: datetime.now(UTC))

    @classmethod
    def reference_frame(cls, objects: QuerySet | None = None) -> pd.DataFrame:
        """Create a DataFrame containing reference data for each document.

        Args:
            objects: QuerySet of documents to include (defaults to all documents of this class)

        Returns:
            pd.DataFrame: DataFrame with reference data, indexed by document name

        """
        objects = objects or cls.objects

        # Create a DataFrame with each column representing a document's reference data
        frame = pd.DataFrame(
            {obj.name: pd.Series(dict(obj.reference.items()), dtype=object) for obj in objects}
        ).transpose()

        # Set the index name to the lowercase class name
        frame.index.name = cls.__name__.lower()
        return frame.sort_index()

    @classmethod
    def subset(cls, names: list[str] | None = None) -> QuerySet:
        """Extract a subset of documents from the database.

        Args:
            names: List of document names to include (defaults to all documents)

        Returns:
            QuerySet: Filtered set of documents

        """
        if names is None:
            return cls.objects

        # Filter objects by name using MongoDB's $in operator
        return cls.objects(name__in=names)

    @classmethod
    def to_dict(cls, objects: QuerySet | None = None) -> dict[str, XDocument]:
        """Create a dictionary of documents with names as keys.

        Args:
            objects: QuerySet of documents to include (defaults to all documents of this class)

        Returns:
            Dict[str, XDocument]: Dictionary mapping document names to document objects

        """
        # Represent all documents of a class as a dictionary for easy lookup
        objects = objects or cls.objects
        return {x.name: x for x in objects}

    @classmethod
    def apply(
        cls, func: Callable[[XDocument], Any], default: Any, objects: QuerySet | None = None
    ) -> Iterator[tuple[str, Any]]:
        """Apply a function to each document, yielding name and result pairs.

        If the function raises an exception for a document, yields the default value instead.

        Args:
            func: Function to apply to each document
            default: Default value to use if the function raises an exception
            objects: QuerySet of documents to process (defaults to all documents of this class)

        Yields:
            Tuple[str, Any]: Pairs of (document_name, function_result)

        """
        objects = objects or cls.objects

        for obj in objects:
            try:
                yield obj.name, func(obj)
            except (TypeError, AttributeError, KeyError):
                # If the function fails, yield the default value
                yield obj.name, default

    @classmethod
    def frame(cls, series: str, key: str, objects: QuerySet | None = None) -> pd.DataFrame:
        """Create a DataFrame from a specific field and key across multiple documents.

        Args:
            series: Name of the field to extract from each document
            key: Key within the field to extract
            objects: QuerySet of documents to include (defaults to all documents of this class)

        Returns:
            pd.DataFrame: DataFrame with columns named by document names and values from the specified field/key

        """
        objects = objects or cls.objects

        # Extract the specified series and key from each document
        # Drop columns that contain only NaN values
        return pd.DataFrame({p.name: getattr(p, series)[key] for p in objects}).dropna(axis=1, how="all")

    def __lt__(self, other: XDocument) -> bool:
        """Compare documents by name for sorting.

        Args:
            other: Another document to compare with

        Returns:
            bool: True if this document's name is lexicographically less than the other's

        """
        return self.name < other.name

    def __eq__(self, other: Any) -> bool:
        """Check if two documents are equal.

        Two documents are equal if they are of the same class and have the same name.

        Args:
            other: Another object to compare with

        Returns:
            bool: True if the documents are equal

        """
        # Two documents are the same if they have the same name and class
        return self.__class__ == other.__class__ and self.name == other.name

    def __hash__(self) -> int:
        """Generate a hash value for the document.

        This allows documents to be used in sets and as dictionary keys.

        Returns:
            int: Hash value based on the document's JSON representation

        """
        return hash(self.to_json(json_options=RELAXED_JSON_OPTIONS))

    def __str__(self) -> str:
        """Generate a string representation of the document.

        Returns:
            str: String in the format "<ClassName: document_name>"

        """
        return f"<{self.__class__.__name__}: {self.name}>"

    def __repr__(self) -> str:
        """Generate a representation of the document for debugging.

        Returns:
            str: String in the format "<ClassName: document_name>"

        """
        return f"<{self.__class__.__name__}: {self.name}>"
