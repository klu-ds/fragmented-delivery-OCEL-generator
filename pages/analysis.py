import dash
from dash import html, dcc, Input, Output, State
from dash import dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import json
import os
import pm4py
import callbacks

dash.register_page(__name__, path="/analysis")

layout = dbc.Container([
    html.H4("Explore OCEL"),
    dbc.Button("Show OCEL Table", id='show-ocel-button', color='secondary'),
    html.Div(id="ocel-table-container"),
    dcc.Store(id="stored-ocel", storage_type="session")
])
