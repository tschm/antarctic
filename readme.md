# [Antarctic](https://tschm.github.io/antarctic/book)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Book](https://github.com/tschm/antarctic/actions/workflows/book.yml/badge.svg)](https://github.com/tschm/antarctic/actions/workflows/book.yml)
[![Release](https://github.com/tschm/antarctic/workflows/Release/badge.svg)](https://github.com/tschm/antarctic/actions/)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/tschm/TinyCTA/main.svg)](https://results.pre-commit.ci/latest/github/tschm/TinyCTA/main)

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/tschm/antarctic)

Project to persist Pandas data structures in a MongoDB database.

## Installation

```python
pip install antarctic
```

## Usage

This project (unless the popular arctic project which I admire)
is based on top of [MongoEngine](https://pypi.org/project/mongoengine/).
MongoEngine is an ORM for MongoDB. MongoDB stores documents.
We introduce a new field and extend the Document class
to make Antarctic a convenient choice for storing Pandas (time series) data.

### Fields

We introduce first a new field --- the PandasField.

```python
from mongoengine import Document, connect
from antarctic.pandas_field import PandasField

# connect with your existing MongoDB
# (here I am using a popular interface mocking a MongoDB)
client = connect(db="test", host="mongomock://localhost")

# Define the blueprint for a portfolio document
class Portfolio(Document):
 nav = PandasField()
 weights = PandasField()
 prices = PandasField()
```

The portfolio objects works exactly the way you think it works

```python

p = Portfolio()
p.nav = pd.Series(...).to_frame(name="nav")
p.prices = pd.DataFrame(...)
p.save()

print(p.nav["nav"])
print(p.prices)
```

Behind the scenes we convert the Frame objects
into parquet bytestreams and
store them in a MongoDB database.

The format should also be readable by R.

#### Documents

In most cases we have copies of very similar documents,
e.g. we store Portfolios and Symbols rather than just a Portfolio or a Symbol.
For this purpose we have developed the abstract `XDocument` class
relying on the Document class of MongoEngine.
It provides some convenient tools to simplify looping
over all or a subset of Documents of the same type, e.g.

```python
from antarctic.document import XDocument
from antarctic.pandas_field import PandasField

client = connect(db="test", host="mongodb://localhost")

class Symbol(XDocument):
 price = PandasField()
```

We define a bunch of symbols and assign a price for each (or some of it):

```python
s1 = Symbol(name="A", price=pd.Series(...).to_frame(name="price")).save()
s2 = Symbol(name="B", price=pd.Series(...).to_frame(name="price")).save()

# We can access subsets like
for symbol in Symbol.subset(names=["B"]):
 print(symbol)

# often we need a dictionary of Symbols:
Symbol.to_dict(objects=[s1, s2])

# Each XDocument also provides a field for reference data:
s1.reference["MyProp1"] = "ABC"
s2.reference["MyProp2"] = "BCD"

# You can loop over (subsets) of Symbols and extract reference and/or series data
print(Symbol.reference_frame(objects=[s1, s2]))
print(Symbol.frame(series="price", key="price"))
print(Symbol.apply(func=lambda x: x.price["price"].mean(), default=np.nan))
```

The XDocument class is exposing DataFrames both for reference and time series data.
There is an `apply` method for using a function on (subset) of documents.

### Database vs. Datastore

Storing json or bytestream representations of Pandas objects
is not exactly a database. Appending is rather expensive as one would have
to extract the original Pandas object, append to it and convert
the new object back into a json or bytestream representation.
Clever sharding can mitigate such effects but at the end of the day
you shouldn't update such objects too often. Often practitioners
use a small database for recording (e.g. over the last 24h) and
update the MongoDB database once a day. It's extremely fast
to read the Pandas objects out of such a construction.

Often such concepts are called DataStores.

## uv

Starting with

```bash
make install
```

will install [uv](https://github.com/astral-sh/uv) and create
the virtual environment defined in
pyproject.toml and locked in uv.lock.

## marimo

We install [marimo](https://marimo.io) on the fly within the aforementioned
virtual environment. Executing

```bash
make marimo
```

will install and start marimo.
