# Antarctic
[![CI](https://github.com/tschm/antarctic/workflows/CI/badge.svg)](https://github.com/tschm/antarctic/actions/)
[![Release](https://github.com/tschm/antarctic/workflows/Release/badge.svg)](https://github.com/tschm/antarctic/actions/)
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/tschm/antarctic/master)

Project to persist Pandas data structures in a MongoDB database. 

## Installation
```python
pip install antarctic
```

###  Usage
This project (unless the popular arctic project which I admire) is based on top of MongoEngine, see [MongoEngine](https://pypi.org/project/mongoengine/).
MongoEngine is an ORM for MongoDB. MongoDB stores documents. We introduce new fields and extend the Document class 
to make Antarctic a convenient choice for storing Pandas (time series) data. 

#### Experiments
We highly recommend to start first with some experiments using the Binder server given above. 


#### Fields
We introduce first two new fields --- one for a Pandas Series and one for a Pandas DataFrame.

```python
from mongoengine import Document, connect
from antarctic.pandas_fields import SeriesField, FrameField

# connect with your existing MongoDB (here I am using a popular interface mocking a MongoDB)
client = connect(db="test", host="mongomock://localhost")


# Define the blueprint for a portfolio document
class Portfolio(Document):
	nav = SeriesField()
	weights = FrameField()
	prices = FrameField()
```

The portfolio objects works exactly the way you think it works

```python

p = Portfolio()
p.nav = pd.Series(...)
p.prices = pd.DataFrame(...)
p.save()

print(p.nav)
print(p.prices)
```

Behind the scenes we convert the both Series and Frame objects into json documents and
store them in a MongoDB database.

Unfortunately it is rather slow to write json documents to disk. We therefore introduce 
the `ParquteFrameField`, the `ParquetSeriesField` and the `PicklePandasField`. In our first experiments the PicklePandasField is the fastest option and
outperforms arctic. However, further work and experiments are required. 

The `ParquetFrameField` relies on a popular format which should also be readable by R. 
Here the frame is converted in a bytestream rather than a json document. Users gain speed, save space and it's possible to work with larger frames.
```python
class Maffay(Document):
    # we support the engine and compression argument as in .to_parquet in pandas
    frame = ParquetFrameField(engine="pyarrow", compression=None)
    
maffay = Maffay()

# the magic happens in the background. The frame is converted in parquet byte stream and stored in the MongoDB.    
maffay.frame = pd.DataFrame(...) # some very large DataFrame, note that column names have to strings.

# reading the frame applies the same magic again.
print(maffay.frame)
```

#### Documents
In most cases we have copies of very similar documents, e.g. we store Portfolios and Symbols rather than just a Portfolio or a Symbol.
For this purpose we have developed the abstract `XDocument` class relying on the Document class of MongoEngine.
It provides some convenient tools to simplify looping over all or a subset of Documents of the same type, e.g.

```python
from antarctic.document import XDocument
from antarctic.pandas_fields import SeriesField

client = connect(db="test", host="mongomock://localhost")


class Symbol(XDocument):
	price = SeriesField()
```
We define a bunch of symbols and assign a price for each (or some of it):

```python
s1 = Symbol(name="A", price=pd.Series(...)).save()
s2 = Symbol(name="B", price=pd.Series(...)).save()

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
print(Symbol.series(series="price"))
print(Symbol.apply(func=lambda x: x.price.mean(), default=np.nan))
```

The XDocument class is exposing DataFrames both for reference and time series data.
There is an `apply` method for using a function on (subset) of documents. 



### Database vs. Datastore

Storing json or bytestream representations of Pandas objects is not exactly a database. Appending is rather expensive as one would have
to extract the original Pandas object, append to it and convert the new object back into a json or bytestream representation.
Clever sharding can mitigate such effects but at the end of the day you shouldn't update such objects too often. Often practitioners
use a small database for recording (e.g. over the last 24h) and update the MongoDB database once a day. It's extremely fast to read the Pandas objects
out of such a construction.

Often such concepts are called DataStores.
