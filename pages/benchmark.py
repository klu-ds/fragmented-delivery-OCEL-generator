from dash import dcc, html, Input, Output, State, register_page
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

from simulation.benchmark import run_grid, summarize, FixedParams

register_page(__name__, path="/benchmark", name="Benchmark")

layout = dbc.Container([
    html.H2("Scalability Benchmark", className="mb-4"),

    dbc.Row([
        dbc.Col([
            dbc.Label("Days range (comma-separated)"),
            dbc.Input(id="benchmark-days", type="text", value="100,200,300"),
        ], md=4),
        dbc.Col([
            dbc.Label("SKUs range (comma-separated)"),
            dbc.Input(id="benchmark-skus", type="text", value="10,20,30"),
        ], md=4),
        dbc.Col([
            dbc.Label("Splits range (comma-separated)"),
            dbc.Input(id="benchmark-splits", type="text", value="1,2,3"),
        ], md=4),
    ], className="mb-3"),

    dbc.Row([
        dbc.Col([
            dbc.Label("Repeats per config"),
            dbc.Input(id="benchmark-repeats", type="number", value=2),
        ], md=4),
    ], className="mb-3"),

    dbc.Button("Run Benchmark", id="run-benchmark", color="primary", className="mb-3"),
    dbc.Button("Cancel Benchmark", id="cancel-benchmark", color="primary", className="mb-3"),
    
    dbc.Row([dbc.Col([
        dbc.Progress(id='progress-bar', style={'margin-top': 15})
    ], width=2)]),
# Hidden storage for raw benchmark data
    dcc.Store(id="benchmark-raw"),

    # Download component
    dcc.Download(id="download-benchmark"),

    dbc.Button("Download Results as CSV", id="download-btn", color="secondary", className="mb-3"),

    html.Div(id="benchmark-results")
], fluid=True)