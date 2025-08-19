from dash import Dash, html, dcc, Input, Output, State, dash_table, page_container, DiskcacheManager, CeleryManager, Dash
from datetime import datetime
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import os
import json
import callbacks

if 'REDIS_URL' in os.environ:
    # Use Redis & Celery if REDIS_URL set as an env variable
    from celery import Celery
    celery_app = Celery(__name__, broker=os.environ['REDIS_URL'], backend=os.environ['REDIS_URL'])
    background_callback_manager = CeleryManager(celery_app)

else:
    # Diskcache for non-production apps when developing locally
    import diskcache
    cache = diskcache.Cache("./cache")
    background_callback_manager = DiskcacheManager(cache)

app = Dash(__name__, use_pages=True, pages_folder="pages", external_stylesheets=[dbc.themes.BOOTSTRAP], background_callback_manager=background_callback_manager)
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
