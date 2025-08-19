from dash import Dash, html, dcc, Input, Output, State, dash_table, page_container
from datetime import datetime
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import os
import json
import callbacks



app = Dash(__name__, use_pages=True, pages_folder="pages", external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server  # for deployment

app.layout = dbc.Container([
    html.H2("Warehouse OCEL Simulator"),
    dbc.Nav(
        [
            dbc.NavLink("Simulation", href="/", active="exact"),
            dbc.NavLink("Analysis", href="/analysis", active="exact"),
            dbc.NavLink("Benchmark",href="/benchmark", active="exact" )
        ],
        pills=True
    ),
    html.Hr(),
    dcc.Store(id="stored-ocel", storage_type="session"),
    dcc.Store(id="stored-sku-configs", storage_type="session"),
    page_container
], fluid=True)

if __name__ == '__main__':
    app.run(debug=True)
