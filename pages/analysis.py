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
    dbc.Button("Show OCEL Table & Stats", id='show-ocel-button', color='secondary'),
    dbc.Button("Download OCEL", id="download-ocel-btn", color="primary", className="mb-3"),
    dcc.Download(id="download-ocel"),
    html.Hr(),
    html.Div(id="ocel-table-container"),
    html.Div(id="ocel-stats-container"),
    dcc.Store(id="stored-ocel", storage_type="session")
])
