from dash import Dash, html, dcc, Input, Output, dash_table
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from decimal import Decimal
import pandas as pd
import requests 
import math


app = Dash(external_stylesheets=[dbc.themes.CYBORG])

app.layout = html.Div(
    
)

if __name__ == "__main__":
    app.run_server(debug=True)