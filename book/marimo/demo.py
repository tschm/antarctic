# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo==0.14.9",
#     "pandas==2.3.0",
#     "mongoengine==0.29.1",
#     "mongomock==4.3.0",
#     "antarctic==0.7.34",
# ]
# ///

import marimo

__generated_with = "0.14.9"
app = marimo.App()

with app.setup:
    import marimo as mo
    import pandas as pd
    from mongoengine import connect
    from mongomock import MongoClient
    from antarctic.pandas_field import PandasField


@app.cell
def _():
    # connect with your existing MongoDB (here I am using a popular interface mocking a MongoDB)
    client = connect(db="test", mongo_client_class=MongoClient)
    return client


@app.cell
def _():
    from mongoengine import Document

    class Portfolio(Document):
        nav = PandasField()
        weights = PandasField()
        prices = PandasField()

    return (Portfolio,)


@app.cell
def _():
    ts = pd.read_csv(
        mo.notebook_location() / "public" / "ts.csv", index_col=0, parse_dates=True
    )
    print(ts)
    return (ts,)


@app.cell
def _():
    prices = pd.read_csv(
        mo.notebook_location() / "public" / "price.csv",
        index_col=0,
        parse_dates=True,
        header=0,
    )
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
    return


if __name__ == "__main__":
    app.run()
