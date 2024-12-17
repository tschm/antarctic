import marimo

__generated_with = "0.9.27"
app = marimo.App()


@app.cell
def __(mo):
    mo.md(
        r"""
        # Demo
        """
    )
    return


@app.cell
def __():
    import pandas as pd
    from mongoengine import Document, connect
    from mongomock import MongoClient

    # connect with your existing MongoDB (here I am using a popular interface mocking a MongoDB)
    client = connect(db="test", mongo_client_class=MongoClient)
    return Document, MongoClient, client, connect, pd


@app.cell
def __():
    from antarctic.pandas_field import PandasField

    return (PandasField,)


@app.cell
def __(Document, PandasField):
    class Portfolio(Document):
        nav = PandasField()
        weights = PandasField()
        prices = PandasField()

    return (Portfolio,)


@app.cell
def __(pd):
    ts = pd.read_csv("data/ts.csv", index_col=0, parse_dates=True)
    print(ts)
    return (ts,)


@app.cell
def __(pd):
    prices = pd.read_csv("data/price.csv", index_col=0, parse_dates=True, header=0)
    print(prices)
    return (prices,)


@app.cell
def __(Portfolio, pd, prices, ts):
    portfolio = Portfolio(
        nav=ts,
        prices=prices,
        weights=pd.DataFrame(index=prices.index, columns=prices.columns, data=1.0 / 7),
    )
    portfolio.save()
    return (portfolio,)


@app.cell
def __():
    import marimo as mo

    return (mo,)


if __name__ == "__main__":
    app.run()
