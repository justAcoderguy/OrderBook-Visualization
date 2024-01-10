from dash import Dash, html, dcc, Input, Output, dash_table
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from decimal import Decimal
import pandas as pd
import requests 
import math


app = Dash(external_stylesheets=[dbc.themes.CYBORG])

# Function to make reuseable dropdowns
def dropdown_option(title, options, default_value, _id):
    return html.Div(children=[
        html.H2(title),
        dcc.Dropdown(options=options, value=default_value, id=_id)
    ])

app.layout = html.Div(children=[
    # Parent Div
    html.Div(children=[
        # Ask and Bid table
        html.Div(
            children=[
            dash_table.DataTable(id="ask_table"),
            html.H2(id="mid_price"),
            dash_table.DataTable(id="bid_table"),
            ], style={"width": "20%"}
        ),

        # Aggregate and Pair dropdowns
        html.Div(
            children=[
                dropdown_option("Aggregate Level",
                    options=["0.01", "0.1", "1", "10", "100"],
                    default_value="0.01",
                    _id="aggregation_level"
                ),
                dropdown_option("Pair",
                    options=["ETHUSDT", "BTCUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT", "BDOTDOT"],
                    default_value="ETHUSDT",
                    _id="pair_select"
                ),
                dropdown_option("Quantity Precision",
                    options=["0", "1", "2", "3", "4"],
                    default_value="3",
                    _id="quantity_precision"
                ),
                dropdown_option("Price Precision",
                    options=["0", "1", "2", "3", "4"],
                    default_value="3",
                    _id="price_precision"
                )
            ], style={"padding-left": "50px"}
        ),
    ], style={"display": "flex",
              "justify-content": "center", # horizontally centered
              "align-items": "center", # Vertically centered
              "height": "100vh"}), 

    dcc.Interval(id="timer", interval=3000)
])


"""
Function to set the granularity of the price.
ie. The difference in price between two consecutive levels
of the orderbook ( bid and ask )
"""
def aggregate_levels(levels_df, agg_level=Decimal('0.1'), side="bid"):
    if side == "bid":
        right = False
        label_func = lambda x: x.left
    elif side == "ask":
        right = True
        label_func = lambda x: x.right

    # if min price is 1004.1287. The min_level would be as follows
    # agg_level -> 0.1 would be 1004.0
    # agg_level -> 10 would be 990.0
    # agg_level -> 0.01 would be 1004.11
    min_level = math.floor(Decimal(min(levels_df.price))/agg_level -1)*agg_level
    max_level = math.ceil(Decimal(max(levels_df.price))/agg_level +1)*agg_level

    # all the bins / buckets the prices will be aggregated into depending on agg_level
    level_bounds = [float(min_level + agg_level*x) for x in
                    range(int((max_level - min_level) / agg_level) + 1)]
    
    levels_df["bin"] = pd.cut(levels_df.price, bins=level_bounds, 
                              precision=10, right=right)
    
    levels_df = levels_df.groupby("bin", observed=False).agg(
        quantity = ("quantity", "sum")).reset_index()
    
    levels_df["price"] = levels_df.bin.apply(label_func)

    levels_df = levels_df[levels_df.quantity > 0]
    levels_df = levels_df[["price", "quantity"]]
    
    return levels_df
    


@app.callback(
    Output("bid_table", "data"),
    Output("ask_table", "data"),
    Output("mid_price", "children"),
    Input("aggregation_level", "value"), # Triggers when theres a change in the agg level dropdown
    Input("quantity_precision", "value"),
    Input("price_precision", "value"),
    Input("pair_select", "value"),
    Input("timer", "n_intervals"), # Triggers at an interval set by dcc.interval
)
def update_orderbook(agg_level, quantity_precision, price_precision, pair, interval):
    base_url = "https://api.binance.com"
    order_book_endpoint = "/api/v3/depth"

    orderbook_url = base_url + order_book_endpoint

    levels_to_show = 10

    params = {
        "symbol": pair.upper(),
        "limit": "100",
    }

    data = requests.get(orderbook_url, params=params).json()

    bids_df = pd.DataFrame(data["bids"], columns=["price", "quantity"], dtype=float)
    asks_df = pd.DataFrame(data["asks"], columns=["price", "quantity"], dtype=float)
     
    bids_df = aggregate_levels(bids_df, agg_level=Decimal(agg_level), side="bid")
    asks_df = aggregate_levels(asks_df, agg_level=Decimal(agg_level), side="ask")

    bids_df = bids_df.sort_values("price", ascending=False) # sort values of orderbook in desc
    asks_df = asks_df.sort_values("price", ascending=False) # sort values of orderbook in asc

    # mid_price = (largest bid + smallest ask) / 2
    mid_price = (bids_df.price.iloc[0] + asks_df.price.iloc[-1])/2 

    bids_df = bids_df.iloc[:levels_to_show] # largest of the bids shown
    asks_df = asks_df.iloc[-levels_to_show:] # smallest of the asks shown

    bids_df.quantity = bids_df.quantity.apply(
        lambda x : f"%.{quantity_precision}f" % x)
    asks_df.quantity = asks_df.quantity.apply(
        lambda x : f"%.{quantity_precision}f" % x)
    
    bids_df.price = bids_df.price.apply(
        lambda x : f"%.{price_precision}f" % x)
    asks_df.price = asks_df.price.apply(
        lambda x : f"%.{price_precision}f" % x)
    
    mid_price = f"%.{price_precision}f" % mid_price

    return bids_df.to_dict("records"), asks_df.to_dict("records"), mid_price  # converts to list of dictionaries


if __name__ == "__main__":
    app.run_server(debug=True)
