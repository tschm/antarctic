"""
Antarctic - A library for persisting Pandas data structures in MongoDB.

This package provides tools for storing and retrieving pandas DataFrames in MongoDB,
using MongoEngine as an Object-Document Mapper (ODM). It includes a custom field type
for pandas DataFrames and an extended Document class with additional functionality.

Main components:
- PandasField: A custom MongoEngine field for storing pandas DataFrames
- XDocument: An abstract base class extending MongoEngine's Document with additional functionality
"""

import importlib.metadata

__version__ = importlib.metadata.version("antarctic")
