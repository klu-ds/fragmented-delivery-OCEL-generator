from dash import callback, dcc, html, Input, Output, State, DiskcacheManager, CeleryManager, Dash, no_update
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import time
import os

from simulation.benchmark import run_grid, summarize, FixedParams

def parse_input(value):
    """Convert a Dash Input value to a list of ints."""
    if isinstance(value, str):
        return [int(x.strip()) for x in value.split(",") if x.strip()]
    elif isinstance(value, int):
        return [value]
    elif isinstance(value, list):
        return [int(x) for x in value]
    return []

def parse_single_int(value, default=1):
    """Safely parse a single integer input from Dash."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default

@callback(
    Output("benchmark-results", "children"),
    Output("benchmark-raw", "data"), 
    Input("run-benchmark", "n_clicks"),
    State("benchmark-days", "value"),
    State("benchmark-skus", "value"),
    State("benchmark-splits", "value"),
    State("benchmark-repeats", "value"),
    background=True,
    running=[
        (Output("run-benchmark", "disabled"), True, False),
        (Output("cancel-benchmark", "disabled"), False, True),
        (
            Output("benchmark-results", "style"),
            {"visibility": "hidden"},
            {"visibility": "visible"},
        ),
        (
            Output("progress-bar", "style"),
            {"visibility": "visible"},
            {"visibility": "hidden"},
        ),
    ],
    cancel=Input("cancel-benchmark", "n_clicks"),
    progress=[Output("progress-bar", "value"), Output("progress-bar", "max")],
    prevent_initial_call=True
)
def run_benchmark(set_progress,n_clicks, days_val, skus_val, splits_val, repeats_val):
    days_list = parse_input(days_val)
    skus_list = parse_input(skus_val)
    splits_list = parse_input(splits_val)
    repeats = parse_single_int(repeats_val, default=1)

    fixed = FixedParams(seed=1, delivery_func_name="constant", verbose=False, write_output=False)
    print(set_progress)
    results = run_grid(days_list, skus_list, splits_list, repeats, fixed, on_progress=set_progress)

    summary = summarize(results)

    table = dbc.Table.from_dataframe(summary.round(3), striped=True, bordered=True, hover=True, size="sm")

    fig = px.line(
            summary,
            x="days",
            y="mean",
            color="n_skus",
            line_dash="split_centre",
            markers=True,
            title="Benchmark Runtime Scaling",
            labels={"mean": "Runtime (s)", "days": "Simulation Days", "n_skus": "# SKUs", "split_centre": "Split Centre"}
        )
    
    # Plot 1: Days vs Runtime
    fig_days = px.line(summary, x="days", y="mean", color="n_skus", line_group="split_centre",
                       markers=True, title="Runtime vs Days")

    # Plot 2: SKUs vs Runtime
    fig_skus = px.line(summary, x="n_skus", y="mean", color="days", line_group="split_centre",
                       markers=True, title="Runtime vs SKUs")

    # Plot 3: Splits vs Runtime
    fig_splits = px.line(summary, x="split_centre", y="mean", color="days", line_group="n_skus",
                         markers=True, title="Runtime vs Splits")

    plots = html.Div([
        dcc.Graph(id="benchmark-graph", figure=fig),
        dcc.Graph(id="days-graph", figure=fig_days),
        dcc.Graph(id="sku-graph", figure=fig_skus),
        dcc.Graph(id="splits-graph", figure=fig_splits),
    ])

    output_div = html.Div([
        html.H5("Benchmark Summary"),
        table,
        html.Hr(),
        plots
    ])

    return output_div, results.to_json(date_format="iso", orient="split")

@callback(
    Output("download-benchmark", "data"),
    Input("download-btn", "n_clicks"),
    State("benchmark-raw", "data"),
    prevent_initial_call=True
)
def download_benchmark(n_clicks, raw_json):
    if raw_json is None:
        print("no data")
        return no_update

    df = pd.read_json(raw_json, orient="split")
    return dcc.send_data_frame(df.to_csv, "benchmark_results.csv")