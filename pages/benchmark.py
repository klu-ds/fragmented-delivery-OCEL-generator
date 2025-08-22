from dash import dcc, html, Input, Output, State, register_page
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

from simulation.benchmark import run_grid, summarize, FixedParams

register_page(__name__, path="/benchmark", name="Benchmark")

layout = dbc.Container([
    html.H2("Scalability Benchmark", className="mb-4"),

    # Config
    dbc.Card([
        dbc.CardHeader("Benchmark Parameters"),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    dbc.Label("Days range (comma-separated)"),
                    dbc.Input(id="benchmark-days", type="text", value="100,500,1000,2000,5000"),
                ], md=4),
                dbc.Col([
                    dbc.Label("Items range (comma-separated)"),
                    dbc.Input(id="benchmark-skus", type="text", value="1,5,10,20,50"),
                ], md=4),
                dbc.Col([
                    dbc.Label("Splits range (comma-separated)"),
                    dbc.Input(id="benchmark-splits", type="text", value="0,1,2,5,10"),
                ], md=4),
            ], className="mb-3"),
            dbc.Row([
                dbc.Col([
                    dbc.Label("Repeats per config"),
                    dbc.Input(id="benchmark-repeats", type="number", value=3),
                ], md=4),
            ]),
        ])
    ], className="mb-4"),

    # Action bar
    dbc.Row([
        dbc.Col([
            dbc.Button("Run Benchmark", id="run-benchmark", color="success", className="me-2"),
            dbc.Button("Cancel Benchmark", id="cancel-benchmark", color="danger", className="me-2"),
            dbc.Button("Download Results as CSV", id="download-btn", color="secondary"),
        ], width="auto")
    ], className="mb-3"),

    # Progress bar
    dbc.Row([
        dbc.Col([
            dbc.Progress(id='progress-bar', style={'margin-top': 10, 'visibility': 'hidden'})
        ], md=6)
    ], className="mb-4"),

    # Results
    dbc.Card([
        dbc.CardHeader("Benchmark Results"),
        dbc.CardBody([
            html.Div(id="benchmark-results")
        ])
    ], className="mb-4"),

    dcc.Store(id="benchmark-raw"),
    dcc.Download(id="download-benchmark")
],)