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
    html.H2("OCEL Analysis", className="mb-4"),

    # Action bar
    dbc.Row([
        dbc.Col([
            dbc.Button("Show OCEL Table & Stats", id='show-ocel-button', color='secondary', className="me-2"),
            dbc.Button("Download OCEL", id="download-ocel-btn", color="primary"),
            dcc.Download(id="download-ocel")
        ], width="auto")
    ], className="mb-4"),

    # Output
    dbc.Card([
        dbc.CardHeader("OCEL Data"),
        dbc.CardBody([
            html.Div(id="ocel-table-container", className="mb-3"),
            html.Div(id="ocel-stats-container")
        ])
    ], className="mb-4"),

    dcc.Store(id="stored-ocel", storage_type="session")
])
