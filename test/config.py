import json
import os
import pandas as pd
import pytest

import random
import string


def random_string(n=5):
    # create a random string of length n
    return ''.join(random.choice(string.ascii_lowercase) for i in range(n))


def resource(name):
    return os.path.join(os.path.dirname(__file__), "resources", name)


def read_pd(name, **kwargs):
    return pd.read_csv(resource(name), **kwargs)


from mongoengine import *
client = connect(db=random_string(5), host="mongomock://localhost")


def read_json(name):
    with open(resource(name)) as f:
        return json.load(f)

