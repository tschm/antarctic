from pathlib import Path

import pytest



@pytest.fixture(scope="session", name="resource_dir")
def resource_fixture():
    """resource fixture"""
    return Path(__file__).parent / "resources"

#def resource(name):
#    return os.path.join(os.path.dirname(__file__), "resources", name)


#def read_pd(name, **kwargs):
#    return pd.read_csv(resource(name), **kwargs)




