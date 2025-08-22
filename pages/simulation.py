from dash import Dash, html, dcc, Input, Output, State, dash_table, register_page
from datetime import datetime
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import os
import json
import pm4py
import callbacks
from simulation import warehouse, simulation

register_page(__name__, path="/")

layout = dbc.Container([
    html.H2("Warehouse Simulation Configurator", className="mb-4"),

    # General Config
    dbc.Card([
        dbc.CardHeader("Simulation Parameters"),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    dbc.Label("Start Date"),
                    dcc.DatePickerSingle(id='start-date', date=datetime.today())
                ], md=4),
                dbc.Col([
                    dbc.Label("Simulation Days"),
                    dbc.Input(id='sim-days', type='number', value=1000)
                ], md=4),
                dbc.Col([
                    dbc.Label("Random Seed"),
                    dbc.Input(id='seed', type='number', value=1)
                ], md=4),
            ], className="mb-3"),
            dbc.Row([
                dbc.Col([
                    dbc.Label("Output Label"),
                    dbc.Input(id='output-label', type='text', value="experiment")
                ], md=6),
            ]),
        ])
    ], className="mb-4"),

    # Item Config
    dbc.Card([
        dbc.CardHeader("Configure Items"),
        dbc.CardBody([
            html.Div(id="sku-config-container"),
            dbc.Button("Add Item", id="add-sku-button", color="primary", className="mt-2"),
        ])
    ], className="mb-4"),

    # Actions
    dbc.Row([
        dbc.Col([
            dbc.Button("Run Simulation", id='run-button', color='success', size="lg"),
        ], width="auto")
    ], className="mb-4"),

    # Output
    dbc.Card([
        dbc.CardHeader("Simulation Results"),
        dbc.CardBody([
            html.Div(id='simulation-output')
        ])
    ], className="mb-4"),

    dcc.Store(id="stored-ocel", storage_type="session"),
])
