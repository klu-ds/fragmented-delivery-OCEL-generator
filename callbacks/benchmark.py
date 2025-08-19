from dash import callback,dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

from simulation.benchmark import run_grid, summarize, FixedParams

@callback(
    Output("benchmark-summary", "children"),
    Output("benchmark-plot", "figure"),
    Output("benchmark-raw", "data"),
    Input("run-benchmark", "n_clicks"),
    State("bm-days", "value"),
    State("bm-skus", "value"),
    State("bm-splits", "value"),
    State("bm-repeats", "value"),
    prevent_initial_call=True
)

def run_benchmark(n_clicks, days_val, skus_val, splits_val, repeats):
    # parse comma-separated values
    days_list = [int(x.strip()) for x in days_val.split(",") if x.strip()]
    skus_list = [int(x.strip()) for x in skus_val.split(",") if x.strip()]
    split_list = [float(x.strip()) for x in splits_val.split(",") if x.strip()]

    fixed = FixedParams(seed=1, delivery_func_name="constant", verbose=False, write_output=False)

    df = run_grid(days_list, skus_list, split_list, repeats, fixed)
    summary = summarize(df)

    # summary table
    table = dbc.Table.from_dataframe(summary.round(3), striped=True, bordered=True, hover=True, size="sm")

    # plot runtime scaling
    fig = px.line(
        summary,
        x="days", y="mean",
        color="n_skus",
        line_dash="split_centre",
        markers=True,
        title="Benchmark Runtime Scaling",
        labels={"mean": "Runtime (s)", "days": "Simulation Days", "n_skus": "# SKUs", "split_centre": "Split Centre"}
    )

    # store raw df in JSON for download
    return table, fig, df.to_json(date_format="iso", orient="split")


@callback(
    Output("download-benchmark", "data"),
    Input("download-btn", "n_clicks"),
    State("benchmark-raw", "data"),
    prevent_initial_call=True
)
def download_benchmark(n_clicks, raw_json):
    if raw_json is None:
        return dash.no_update

    df = pd.read_json(raw_json, orient="split")
    return dcc.send_data_frame(df.to_csv, "benchmark_results.csv")