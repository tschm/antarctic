# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo==0.14.9",
#     "pandas==2.3.0",
#     "polars==1.31.0",
#     "pyarrow==20.0.0",
# ]
# ///

import marimo

__generated_with = "0.10.10"
app = marimo.App()

with app.setup:
    import marimo as mo
    import pandas as pd


@app.cell
def _():
    from mongoengine import Document, connect
    from mongomock import MongoClient

    # connect with your existing MongoDB (here I am using a popular interface mocking a MongoDB)
    client = connect(db="test", mongo_client_class=MongoClient)
    return Document, MongoClient, client, connect


@app.cell
def _():
    from antarctic.pandas_field import PandasField

    return (PandasField,)


@app.cell
def _(Document, PandasField):
    class Portfolio(Document):
        nav = PandasField()
        weights = PandasField()
        prices = PandasField()

    return (Portfolio,)


@app.cell
def _():
    ts = pd.read_csv("public/ts.csv", index_col=0, parse_dates=True)
    print(ts)
    return (ts,)


@app.cell
def _():
    prices = pd.read_csv("public/price.csv", index_col=0, parse_dates=True, header=0)
    print(prices)
    return (prices,)


@app.cell
def _(Portfolio, prices, ts):
    portfolio = Portfolio(
        nav=ts,
        prices=prices,
        weights=pd.DataFrame(index=prices.index, columns=prices.columns, data=1.0 / 7),
    )
    portfolio.save()
    return (portfolio,)


if __name__ == "__main__":
    app.run()
