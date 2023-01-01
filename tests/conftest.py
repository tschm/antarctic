from pathlib import Path

import pytest
from mongoengine import connect, disconnect


@pytest.fixture(scope="session", name="resource_dir")
def resource_fixture():
    """resource fixture"""
    return Path(__file__).parent / "resources"

@pytest.fixture(scope="function", name="client")
def client_fixture():
    x = connect(db="test_pandas", host="mongodb://localhost")
    yield x
    disconnect()

#def resource(name):
#    return os.path.join(os.path.dirname(__file__), "resources", name)


#def read_pd(name, **kwargs):
#    return pd.read_csv(resource(name), **kwargs)




