import datetime
import pandas as pd

from mongoengine import *

# We rely heavily on MongoEngine, see http://mongoengine.org/
# MongoEngine is an ORM for MongoDB, as sqlalchemy is an ORM for SQL
# MongoDB is a document based database.
# There is a one-to-one relationship between documents and objects.
# The objects are defined using MongoEngine


# An document could be
# {"Name": "IBM US Equity", "PX_LAST": 110.0, ...}

# Each document is dynamic and stores all time series and reference data related to an object
# Each object and therefore each document is a child of the abstract PandasDocument object.
from numpy import float64


class PandasDocument(DynamicDocument):
    # A PandasDocument is an abstract Mongo Document, e.g. instances of this document can not be instantiated.
    # All concrete objects such as Symbols or Strategies are children of the PandasDocument.
    # Having a common parent helps to share functionality
    meta = {'abstract': True}
    # Each children has a unique name (within the class of the children)
    name = StringField(max_length=200, required=True, unique=True)
    # A dictionary for reference data, e.g. something like symbol.reference["PX_LAST"] = ...
    reference = DictField()
    # Date modified
    date_modified = DateTimeField(default=datetime.datetime.utcnow)

    @classmethod
    def reference_frame(cls, products=None) -> pd.DataFrame:
        products = products or cls.objects

        frame = pd.DataFrame(
            {product.name: pd.Series({key: data for key, data in product.reference.items()}) for product in
             products}).transpose()
        frame.index.name = cls.__name__.lower()
        return frame.sort_index()

    def __lt__(self, other):
        # sort documents by name
        return self.name < other.name

    def __eq__(self, other):
        # two documents are the sname if they have the same name and class
        return self.__class__ == other.__class__ and self.name == other.name

    # we want to make a set of assets, etc....
    def __hash__(self):
        return hash(self.to_json())

    def __setattr__(self, key, value):
        if isinstance(value, pd.Series):
            DynamicDocument.__setattr__(self, key, value.to_json(orient="split"))
        elif isinstance(value, pd.DataFrame):
            DynamicDocument.__setattr__(self, key, value.to_json(orient="split"))
        else:
            DynamicDocument.__setattr__(self, key, value)

    def __getattribute__(self, item):
        if item.startswith("_"):
            return DynamicDocument.__getattribute__(self, item)

        x = DynamicDocument.__getattribute__(self, item)

        try:
            return pd.read_json(x, orient="split", typ="frame")
        except:
            pass

        try:
            return pd.read_json(x, orient="split", typ="series")
        except:
            pass

        return x

    @classmethod
    def products(cls, names=None):
        # extract symbols from database
        if names is None:
            return cls.objects
        else:
            return cls.objects(name__in=names)

    @classmethod
    def pandas_frame(cls, item, products=None) -> pd.DataFrame:
        products = products or cls.objects
        frame = pd.DataFrame({product.name: product.__pandas(item=item, default=pd.Series({}, dtype=float64)) for product in products})
        frame = frame.dropna(axis=1, how="all").transpose()
        frame.index.name = cls.__name__.lower()
        return frame.sort_index().transpose()

    def __pandas(self, item, default=None):
        try:
            obj = self.__getattribute__(item)
            if isinstance(obj, pd.Series) or isinstance(obj, pd.DataFrame):
                return obj

            raise AttributeError()
        except AttributeError:
            return default

    def __str__(self):
        return "<{type}: {name}>".format(type=self.__class__.__name__, name=self.name)

    @classmethod
    def to_dict(cls):
        # represent all documents of a class as a dictionary
        return {x.name: x for x in cls.objects}
