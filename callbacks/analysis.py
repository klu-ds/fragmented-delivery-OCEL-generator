from dash import callback, Output, Input, State, html, dcc, dash_table
import pandas as pd
import pm4py
import plotly.express as px
from collections import Counter
import dash_bootstrap_components as dbc
import json

def ocel_summary_table(ocel):
    """
    Builds a dbc.Table with the same information from pm4py OCEL.get_summary(),
    but in structured format.
    """
    # Compute summary stats
    num_events = len(ocel.events)
    num_objects = len(ocel.objects)
    num_activities = ocel.events[ocel.event_activity].nunique()
    num_object_types = ocel.objects[ocel.object_type_column].nunique()
    num_event_object_rels = len(ocel.relations)

    activities_occ = Counter(ocel.events[ocel.event_activity].value_counts().to_dict())
    object_types_occ = Counter(ocel.objects[ocel.object_type_column].value_counts().to_dict())
    unique_acts_per_obj_type = Counter(
        ocel.relations.groupby(ocel.object_type_column)[ocel.event_activity].nunique().to_dict()
    )

    # General stats table
    general_rows = [
        ("Number of events", num_events),
        ("Number of objects", num_objects),
        ("Number of activities", num_activities),
        ("Number of object types", num_object_types),
        ("Events-objects relationships", num_event_object_rels),
    ]
    general_table = dbc.Table(
        [html.Thead(html.Tr([html.Th("Metric"), html.Th("Value")]))] +
        [html.Tbody([html.Tr([html.Td(k), html.Td(v)]) for k, v in general_rows])],
        bordered=True, striped=True, hover=True, size="sm"
    )

    # Activities occurrences table
    activities_table = dbc.Table(
        [html.Thead(html.Tr([html.Th("Activity"), html.Th("Occurrences")]))] +
        [html.Tbody([html.Tr([html.Td(k), html.Td(v)]) for k, v in activities_occ.items()])],
        bordered=True, striped=True, hover=True, size="sm"
    )

    # Object types occurrences table
    object_types_table = dbc.Table(
        [html.Thead(html.Tr([html.Th("Object Type"), html.Th("Count")]))] +
        [html.Tbody([html.Tr([html.Td(k), html.Td(v)]) for k, v in object_types_occ.items()])],
        bordered=True, striped=True, hover=True, size="sm"
    )

    # Unique activities per object type table
    unique_acts_table = dbc.Table(
        [html.Thead(html.Tr([html.Th("Object Type"), html.Th("Unique Activities")]))] +
        [html.Tbody([html.Tr([html.Td(k), html.Td(v)]) for k, v in unique_acts_per_obj_type.items()])],
        bordered=True, striped=True, hover=True, size="sm"
    )

    # Wrap in cards for nicer layout
    return html.Div([
        dbc.Card(dbc.CardBody([html.H5("General Summary"), general_table]), className="mb-3"),
        dbc.Card(dbc.CardBody([html.H5("Activities Occurrences"), activities_table]), className="mb-3"),
        dbc.Card(dbc.CardBody([html.H5("Object Types Occurrences"), object_types_table]), className="mb-3"),
        dbc.Card(dbc.CardBody([html.H5("Unique Activities per Object Type"), unique_acts_table]), className="mb-3"),
    ])


@callback(
    Output('ocel-table-container', 'children'),
    Output('ocel-stats-container', 'children'),
    Input('show-ocel-button', 'n_clicks'),
    State('stored-ocel', 'data'),
    prevent_initial_call=True
)
def analyze_ocel(n_clicks, ocel_json):
    if not ocel_json:
        return html.P("No OCEL data available. Please run a simulation first."), None, None
    
    # Load OCEL DataFrame
    ocel_df = pd.read_json(ocel_json, orient='split')
    
    # Show OCEL table
    table = dash_table.DataTable(
        id='ocel-table',
        data=ocel_df.to_dict('records'),
        columns=[{"name": i, "id": i} for i in ocel_df.columns],
        page_size=20,
        filter_action="native",
        sort_action="native",
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'left', 'minWidth': '100px', 'width': '150px', 'maxWidth': '300px'}
    )
    
    ocel = pm4py.read_ocel2_json("OCEL.json")
    ocel_summary_component = ocel_summary_table(ocel)
    
    
    return table, ocel_summary_component

@callback(
    Output("download-ocel", "data"),
    Input("download-ocel-btn", "n_clicks"),
    prevent_initial_call=True
)
def download_ocel(n_clicks):
    # Load your OCEL (replace with your actual OCEL object in memory if available)
    with open('OCEL.json', 'r') as file:
        ocel = json.load(file)
    ocel_json = json.dumps(ocel)
    # Return as downloadable file
    return dcc.send_string(
        ocel_json,
        filename="OCEL.json"
    )