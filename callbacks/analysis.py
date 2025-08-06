
from dash import Input, Output, callback, html, State
from dash import dash_table
import pandas as pd

@callback(
    Output('ocel-table-container', 'children'),
    Input('show-ocel-button', 'n_clicks'),
    State('stored-ocel', 'data'),
    prevent_initial_call=True
)
def show_ocel_table(n_clicks, ocel_data):
    if not ocel_data:
        return html.P("No OCEL data available. Please run a simulation first.") 
    ocel_df = pd.read_json(ocel_data, orient='split')
    return dash_table.DataTable(
        id='ocel-table',
        data= ocel_df.to_dict('records'),
        columns=[{"name": i, "id": i} for i in ocel_df.columns],
        page_size=20,
        filter_action="native",
        sort_action="native",
        style_table={'overflowX': 'auto'},
        style_cell={
            'textAlign': 'left',
            'minWidth': '100px',
            'width': '150px',
            'maxWidth': '300px'
        }
    )