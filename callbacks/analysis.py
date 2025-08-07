
# from dash import Input, Output, callback, html, State
# from dash import dash_table
# import pandas as pd

# @callback(
#     Output('ocel-table-container', 'children'),
#     Input('show-ocel-button', 'n_clicks'),
#     State('stored-ocel', 'data'),
#     prevent_initial_call=True
# )
# def show_ocel_table(n_clicks, ocel_data):
#     if not ocel_data:
#         return html.P("No OCEL data available. Please run a simulation first.") 
#     ocel_df = pd.read_json(ocel_data, orient='split')
#     return dash_table.DataTable(
#         id='ocel-table',
#         data= ocel_df.to_dict('records'),
#         columns=[{"name": i, "id": i} for i in ocel_df.columns],
#         page_size=20,
#         filter_action="native",
#         sort_action="native",
#         style_table={'overflowX': 'auto'},
#         style_cell={
#             'textAlign': 'left',
#             'minWidth': '100px',
#             'width': '150px',
#             'maxWidth': '300px'
#         }
#     )

from dash import callback, Output, Input, State, html, dcc, dash_table
import pandas as pd
import pm4py
import plotly.express as px

@callback(
    Output('ocel-table-container', 'children'),
    Output('ocel-stats-container', 'children'),
    Output('pm-variant-plot', 'children'),
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
    
    # Compute basic stats
    num_events = len(ocel_df)
    obj_types = ocel_df['ocel:type'].unique() if 'ocel:type' in ocel_df.columns else []
    num_obj_types = len(obj_types)
    
    # Assuming columns like 'ocel:timestamp' and 'ocel:type' exist; adapt if needed
    time_min = ocel_df['ocel:timestamp'].min() if 'ocel:timestamp' in ocel_df.columns else 'N/A'
    time_max = ocel_df['ocel:timestamp'].max() if 'ocel:timestamp' in ocel_df.columns else 'N/A'
    
    stats = html.Div([
        html.H5("OCEL Summary Statistics"),
        html.P(f"Number of events: {num_events}"),
        html.P(f"Number of distinct object types: {num_obj_types}"),
        html.P(f"Object types: {', '.join(obj_types)}"),
        html.P(f"Event time range: {time_min} to {time_max}")
    ])
    
    # Use pm4py to get variants dataframe for process mining plot
    try:
        # convert ocel_df back to OCEL object for pm4py (you may need to read from json)
        # if you have a pm4py OCEL object you can do:
        ocel_obj = pm4py.read_ocel2_json("OCEL.json")  # or adapt if stored differently
        
        variants_df = pm4py.get_variants_ocel(ocel_obj)
        # Simple bar chart of top variants by frequency
        fig = px.bar(
            variants_df,
            x='variant',
            y='count',
            title="Process Variants Frequencies"
        )
        plot = dcc.Graph(figure=fig)
    except Exception as e:
        plot = html.P(f"Could not generate variant plot: {e}")
    
    return table, stats, plot
