"""overload the document class of MongoEngine"""

from __future__ import annotations

from datetime import datetime

import pandas as pd
from mongoengine import DateTimeField, DictField, Document, StringField


class XDocument(Document):
    """
    A XDocument is an abstract Mongo Document,
    e.g. instances of this document can not be instantiated.
    All concrete objects such as Symbols or Strategies are children of the XDocument.
    Having a common parent helps to share functionality
    """

    meta = {"abstract": True}

    name = StringField(unique=True, required=True)
    reference = DictField()

    # Date modified
    date_modified = DateTimeField(default=datetime.utcnow)

    @classmethod
    def reference_frame(cls, objects=None) -> pd.DataFrame:
        """get a frame of reference data for each object"""
        objects = objects or cls.objects

        frame = pd.DataFrame(
            {
                obj.name: pd.Series(dict(obj.reference.items()), dtype=object)
                for obj in objects
            }
        ).transpose()
        frame.index.name = cls.__name__.lower()
        return frame.sort_index()

    @classmethod
    def subset(cls, names=None):
        """extract a subset of documents from the database"""
        if names is None:
            return cls.objects

        return cls.objects(name__in=names)

    @classmethod
    def to_dict(cls, objects=None):
        """create a dictionary of objects of class cls
        The objects are either given explicitly or if not
        all objects of this particular class are extracted.
        """
        # represent all documents of a class as a dictionary
        objects = objects or cls.objects
        return {x.name: x for x in objects}

    @classmethod
    def apply(cls, func, default, objects=None) -> pd.DataFrame:
        """apply a function func to documents.
        Yield the default document if something went wrong"""
        objects = objects or cls.objects

        for obj in objects:
            try:
                yield obj.name, func(obj)
            except (TypeError, AttributeError, KeyError):
                yield obj.name, default

    @classmethod
    def frame(cls, series, key, objects=None) -> pd.DataFrame:
        """get a series from each document and return a frame of them"""
        objects = objects or cls.objects
        return pd.DataFrame({p.name: getattr(p, series)[key] for p in objects}).dropna(
            axis=1, how="all"
        )

    def __lt__(self, other):
        """sort documents by name"""
        return self.name < other.name

    def __eq__(self, other):
        """two documents are equal if they are of the same class
        and have the same name"""

        # two documents are the sname if they have the same name and class
        return self.__class__ == other.__class__ and self.name == other.name

    # we want to make a set of assets, etc....
    def __hash__(self):
        """hashcode"""
        return hash(self.to_json())

    def __str__(self):
        """string representation of a document"""
        return f"<{self.__class__.__name__}: {self.name}>"

    def __repr__(self):
        """representation of a document"""
        return f"<{self.__class__.__name__}: {self.name}>"
