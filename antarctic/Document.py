import pandas as pd
from mongoengine import *


class XDocument(Document):
    # A XDocument is an abstract Mongo Document, e.g. instances of this document can not be instantiated.
    # All concrete objects such as Symbols or Strategies are children of the XDocument.
    # Having a common parent helps to share functionality
    meta = {'abstract': True}

    name = StringField(unique=True, required=True)
    reference = DictField()

    @classmethod
    def reference_frame(cls, products=None) -> pd.DataFrame:
        products = products or cls.objects

        frame = pd.DataFrame(
            {product.name: pd.Series({key: data for key, data in product.reference.items()}) for product in
             products}).transpose()
        frame.index.name = cls.__name__.lower()
        return frame.sort_index()

    @classmethod
    def products(cls, names=None):
        # extract symbols from database
        if names is None:
            return cls.objects
        else:
            return cls.objects(name__in=names)

    @classmethod
    def to_dict(cls):
        # represent all documents of a class as a dictionary
        return {x.name: x for x in cls.objects}

    @classmethod
    def apply(cls, f, default, products=None) -> pd.DataFrame:
        products = products or cls.objects

        for product in products:
            try:
                yield product.name, f(product)
            except:
                yield product.name, default

    def __lt__(self, other):
        # sort documents by name
        return self.name < other.name

    def __eq__(self, other):
        # two documents are the sname if they have the same name and class
        return self.__class__ == other.__class__ and self.name == other.name

    # we want to make a set of assets, etc....
    def __hash__(self):
        return hash(self.to_json())

    def __str__(self):
        return "<{type}: {name}>".format(type=self.__class__.__name__, name=self.name)