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
This project (unless the popular arctic project which I admire) is based on top of MongoEngine, see https://pypi.org/project/mongoengine/
MongoEngine is an ORM for MongoDB. MongoDB stores documents. 
We introduce here two new fields --- one for a Pandas Series and one for a Pandas DataFrame.

```python
from mongoengine import Document, connect
from antarctic.PandasFields import SeriesField, FrameField

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

We don't apply any clever conversion into compressed bytestreams. Performance is not our main concern here.

### Database?

Storing json or bytestream representations of Pandas objects is not exactly a database. Appending is rather expensive as one would have
to extract the original Pandas object, append to it and convert the new object back into a json or bytestream representation.
Clever sharding can mitigate such effects but at the end of the day you shouldn't update such objects too often. Often practitioners
use a small database for recording (e.g. over the last 24h) and update the MongoDB database once a day. It's extremely fast to read the Pandas objects
out of such a construction.

Also note that in theory one could try to build this on top of pyarrow and support both R and Python. 