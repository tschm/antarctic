import pandas as pd


def merge(new, old=None):
    # very smart merging here, new and old merge
    if new is not None:
        if old is not None:
            x = pd.concat((new, old), sort=True)
            return x.groupby(x.index).first().sort_index()
        else:
            return new

    else:
        return old