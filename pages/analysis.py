import dash
from dash import html, dcc, Input, Output, State
from dash import dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import json
import os
import pm4py
import callbacks
import dash_cytoscape as cyto


dash.register_page(__name__, path="/analysis")

layout = dbc.Container([
    html.H4("Explore OCEL"),
    dbc.Button("Show OCEL Table & Stats", id='show-ocel-button', color='secondary'),
    html.Hr(),
    html.Div(id="ocel-table-container"),
    html.Div(id="ocel-stats-container"),
    dbc.Button("Show OCEL Network", id="show-ocel-network", color='primary'),
    html.Div(id="ocel-network-container"),
    dcc.Store(id="stored-ocel", storage_type="session")
])