"""Antarctic Demo."""
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo==0.14.9",
#     "pandas==2.3.1",
#     "mongoengine==0.29.1",
#     "mongomock==4.3.0",
#     "antarctic==0.7.35",
#     "plotly==6.2.0",
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

    pd.options.plotting.backend = "plotly"


@app.cell
def _():
    # connect with your existing MongoDB (here I am using a popular interface mocking a MongoDB)
    connect(db="test", mongo_client_class=MongoClient)
    return


@app.cell
def _():
    from mongoengine import Document

    class Portfolio(Document):
        # nav = PandasField()
        weights = PandasField()
        prices = PandasField()

        @property
        def nav(self):
            """Compute NAV from weights and prices.

            Returns:
                pd.DataFrame: DataFrame with computed NAV values

            """
            # Ensure weights and prices have the same index and columns
            common_index = self.weights.index.intersection(self.prices.index)
            common_columns = self.weights.columns.intersection(self.prices.columns)

            # Filter weights and prices to common index and columns
            weights = self.weights.loc[common_index, common_columns]
            prices = self.prices.loc[common_index, common_columns]

            # Compute weighted prices (element-wise multiplication)
            weighted_prices = weights * prices

            # Sum across assets to get NAV
            computed_nav = weighted_prices.sum(axis=1).to_frame(name="computed_nav")

            return computed_nav

    return (Portfolio,)


@app.cell
def _():
    prices = pd.read_csv(
        mo.notebook_location() / "public" / "price.csv",
        index_col=0,
        parse_dates=True,
        header=0,
    ).ffill()
    print(prices)
    return (prices,)


@app.cell
def _(Portfolio, prices):
    portfolio = Portfolio(
        prices=prices,
        weights=pd.DataFrame(index=prices.index, columns=prices.columns, data=1.0 / 7),
    )
    portfolio.save()
    portfolio.nav
    return (portfolio,)


@app.cell
def _(portfolio):
    # Plot the nav curve
    portfolio.nav.plot()

    return


if __name__ == "__main__":
    app.run()
