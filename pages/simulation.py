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
    html.H2("Warehouse Simulation Configurator"),
    
    dbc.Row([
        dbc.Col([
            dbc.Label("Start Date"),
            dcc.DatePickerSingle(
                id='start-date',
                date=datetime.today()
            )
        ]),
        dbc.Col([
            dbc.Label("Simulation Days"), 
            dbc.Input(id='sim-days', type='number', value=1750)
        ]),
        dbc.Col([
            dbc.Label("Random Seed"),
            dbc.Input(id='seed', type='number', value=1)
        ]),
    ], className="mb-3"),
    dbc.Row([
        dbc.Col([
            dbc.Label("Output Label"),
            dbc.Input(id='output-label', type='text', value="experiment")
        ]),
    ], className="mb-3"),

    dcc.Store(id="stored-sku-configs", data=[], storage_type="session"),

    html.H4("Configure SKUs"),
    html.Div(id="sku-config-container"),  # where dynamic inputs will appear
    dbc.Button("Add SKU", id="add-sku-button", color="primary", className="mb-2"),

     html.Hr(),
    
    dbc.Button("Run Simulation", id='run-button', color='primary'),

    html.Hr(),

    html.Div(id='simulation-output'),

    dcc.Store(id="stored-ocel", storage_type="session"),

    html.Br()
])


