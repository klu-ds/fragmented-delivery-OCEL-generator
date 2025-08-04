from dash import Dash, html, dcc, Input, Output, State, dash_table
from datetime import datetime
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import os
import json
import pm4py

from simulation.simulation import Simulation
from simulation.warehouse import Warehouse



app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

delivery_functions = {
    '1 (constant)': lambda x: 1,
    'x^2': lambda x: x**2,
    '-log(x)': lambda x: -np.log(x)
}

app.layout = dbc.Container([
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
            dbc.Label("Output Label"),
            dbc.Input(id='output-label', type='text', value="experiment")
        ]),
    ], className="mb-3"),

    dbc.Button("Run Simulation", id='run-button', color='primary'),

    html.Hr(),

    html.Div(id='simulation-output'),

    dcc.Store(id='stored-ocel'),

    html.Br(),

    dbc.Button("Show OCEL Table", id='show-ocel-button', color='secondary'),

    html.Div(id='ocel-table-container')
])

@app.callback(
    Output('simulation-output', 'children'),
    Output('stored-ocel', 'data'),
    Input('run-button', 'n_clicks'),
    State('start-date', 'date'),
    State('sim-days', 'value'),
    State('seed', 'value'),
    State('mean-demand', 'value'),
    State('std-demand', 'value'),
    State('delivery-func', 'value'),
    State('output-label', 'value'),
    prevent_initial_call=True
)
def run_simulation(n_clicks, start_date, days, seed, mean_demand, std_demand, delivery_func_label, output_label):
    if not n_clicks:
        return ""

    # Select function from label
    delivery_func = delivery_functions[delivery_func_label]

    sku_config_0 = {
        'id' : 0,
        'rop' : 500,
        'eoq' : 0,
        'z_score': 1.65,
        'order_base_cost' : 60,
        'holding_cost' : 1 , 
        'inventory' : 500,
        'kpi' : 'order_completion',
        'verbose': True
    }

    sku_config_1 = {
        'id' : 1,
        'rop' : 300,
        'eoq' : 0,
        'z_score': 1.65,
        'order_base_cost' : 30,
        'holding_cost' : 1 , 
        'inventory' : 500,
        'kpi' : 'order_completion',
        'verbose': True
    }

    warehouse = Warehouse([sku_config_0,sku_config_1])

    # Build config
    sim_config = {
        'warehouse' : warehouse,
        'start_date': datetime.fromisoformat(start_date),
        'days': days,
        'seed': seed,
        'mean_daily_demand': mean_demand,
        'std_daily_demand': std_demand,
        'delivery_func': [delivery_func, delivery_func],
        'delivery_split_centre': 0,
        'delivery_split_std': 1,
        'output': output_label
    }


    simulation = Simulation( config=sim_config)
    simulation.run()
    simulation.evaluate_globally(report=True)
    for sku in warehouse.SKUs.keys():
        simulation.evaluate_skus(sku, report=True)

    return (
        html.Div([
            html.H5("Simulation Completed"),
            html.P(f"service level: {simulation.results['service_level']:.2f}"),
            #html.P(f"Item Completion: {kpis['item_completion']:.2f}"),
        ]),
        get_ocel('experiment/')
    )

def get_ocel(path):
    complete_ocel_json = {}
    complete_ocel_json["objects"] = []
    complete_ocel_json["events"] =[]
    o_count = 0
   
    json_files = [pos_json for pos_json in os.listdir(path) if pos_json.endswith('.json')]
    with open(os.path.join(path,json_files[0])) as init_js:
        json_text = json.load(init_js)
        complete_ocel_json["objectTypes"]= json_text["objectTypes"]
        complete_ocel_json["eventTypes"]= json_text["eventTypes"]

    for index, js in enumerate(json_files):
        with open(os.path.join(path, js)) as json_file:
            json_ocel = json.load(json_file)
            o_count += len(json_ocel["objects"])
            complete_ocel_json["objects"] +=(json_ocel["objects"])
            complete_ocel_json["events"]+=(json_ocel["events"])

    # Serializing json
    json_object = json.dumps(complete_ocel_json)

    # Writing to sample.json
    with open("OCEL.json", "w") as outfile:
        outfile.write(json_object)

    ocel = pm4py.read_ocel2_json("OCEL.json").get_extended_table()
    #ocel.columns = [col.split(':')[-1] for col in ocel.columns]
    def serialize_cell(x):
        if isinstance(x, (dict, list)):
            return json.dumps(x)
        elif x is None:
            return ''
        else:
            return str(x)

    for col in ocel.columns:
        ocel[col] = ocel[col].apply(serialize_cell)

    return ocel.to_dict('records')

@app.callback(
    Output('ocel-table-container', 'children'),
    Input('show-ocel-button', 'n_clicks'),
    State('stored-ocel', 'data'),
    prevent_initial_call=True
)
def show_ocel_table(n_clicks, ocel_data):
    if not ocel_data:
        return html.P("No OCEL data available. Please run a simulation first.")

    columns = [{"name": col, "id": col} for col in ocel_data[0].keys()] if ocel_data else []
    


    return dash_table.DataTable(
        id='ocel-table',
        columns=columns,
        data=ocel_data,
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

if __name__ == '__main__':
    app.run(debug=True)
