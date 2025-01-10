import marimo

__generated_with = "0.10.10"
app = marimo.App()


@app.cell
def _(mo):
    mo.md(r"""# Demo""")
    return


@app.cell
def _():
    import pandas as pd
    from mongoengine import Document, connect
    from mongomock import MongoClient

    # connect with your existing MongoDB (here I am using a popular interface mocking a MongoDB)
    client = connect(db="test", mongo_client_class=MongoClient)
    return Document, MongoClient, client, connect, pd


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
def _(pd):
    ts = pd.read_csv("data/ts.csv", index_col=0, parse_dates=True)
    print(ts)
    return (ts,)


@app.cell
def _(pd):
    prices = pd.read_csv("data/price.csv", index_col=0, parse_dates=True, header=0)
    print(prices)
    return (prices,)


@app.cell
def _(Portfolio, pd, prices, ts):
    portfolio = Portfolio(
        nav=ts,
        prices=prices,
        weights=pd.DataFrame(index=prices.index, columns=prices.columns, data=1.0 / 7),
    )
    portfolio.save()
    return (portfolio,)


@app.cell
def _():
    import marimo as mo

    return (mo,)


if __name__ == "__main__":
    app.run()
