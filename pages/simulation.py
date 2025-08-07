from dash import Dash, html, dcc, Input, Output, State, dash_table, register_page
from datetime import datetime
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import os
import json
import pm4py
import callbacks
from simulation import warehouse, simulation

delivery_functions = {
    '1 (constant)': lambda x: 1,
    'x^2': lambda x: x**2,
    '-log(x)': lambda x: -np.log(x)
}

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
            dbc.Label("Mean Daily Demand"),
            dbc.Input(id='mean-demand', type='number', value=50)
        ]),
        dbc.Col([
            dbc.Label("Std Daily Demand"),
            dbc.Input(id='std-demand', type='number', value=1)
        ]),
        dbc.Col([
            dbc.Label("Delivery Function"),
            dcc.Dropdown(
                id='delivery-func',
                options=[{'label': k, 'value': k} for k in delivery_functions.keys()],
                value='1 (constant)'
            )
        ]),
    ], className="mb-3"),
    dbc.Row([
        dbc.Col([
            dbc.Label("Mean amount of splits"),
            dbc.Input(id='mean-split', type='number', value=0)
        ]),
        dbc.Col([
            dbc.Label("Std split"),
            dbc.Input(id='std-split', type='number', value=1)
        ])
    ], className="mb-3"),
    dbc.Row([
        dbc.Col([
            dbc.Label("Output Label"),
            dbc.Input(id='output-label', type='text', value="experiment")
        ]),
    ], className="mb-3"),

    dbc.Button("Run Simulation", id='run-button', color='primary'),

    html.Hr(),

    html.Div(id='simulation-output'),

    dcc.Store(id="stored-ocel", storage_type="session"),

    html.Br()
])


