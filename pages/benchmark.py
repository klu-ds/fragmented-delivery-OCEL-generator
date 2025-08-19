from dash import dcc, html, Input, Output, State, register_page
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

from simulation.benchmark import run_grid, summarize, FixedParams

register_page(__name__, path="/benchmark", name="Benchmark")

layout = dbc.Container([
    html.H2("Scalability Benchmark", className="mb-4"),

    # Controls
    dbc.Row([
        dbc.Col([
            dbc.Label("Simulation Days"),
            dcc.Input(id="bm-days", type="text", value="250,500,1000,2000", className="form-control"),
        ], md=3),

        dbc.Col([
            dbc.Label("Number of SKUs"),
            dcc.Input(id="bm-skus", type="text", value="1,5,10,20", className="form-control"),
        ], md=3),

        dbc.Col([
            dbc.Label("Split Centres"),
            dcc.Input(id="bm-splits", type="text", value="0,1,2,5", className="form-control"),
        ], md=3),

        dbc.Col([
            dbc.Label("Repeats"),
            dcc.Input(id="bm-repeats", type="number", value=3, min=1, className="form-control"),
        ], md=3),
    ], className="mb-3"),

    dbc.Button("Run Benchmark", id="run-benchmark", color="primary", className="mb-3"),

    # Hidden storage for raw benchmark data
    dcc.Store(id="benchmark-raw"),

    # Download component
    dcc.Download(id="download-benchmark"),

    dbc.Button("Download Results as CSV", id="download-btn", color="secondary", className="mb-3"),

    dbc.Spinner(children=[
        html.Div(id="benchmark-summary"),
        dcc.Graph(id="benchmark-plot")
    ])
], fluid=True)