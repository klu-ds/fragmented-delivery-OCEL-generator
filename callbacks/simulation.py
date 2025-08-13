from dash import Input, Output, State, callback, html,  MATCH, ALL, ctx, callback_context
from datetime import datetime
import dash_bootstrap_components as dbc
import os, shutil
import json
import pm4py
from simulation.warehouse import Warehouse
from simulation.simulation import Simulation
import numpy as np

delivery_functions = {
    'constant': lambda x: 1,
    'quadratic': lambda x: x**2,
    'logarithmic': lambda x: -np.log(x)
}
from dash.exceptions import PreventUpdate
@callback(
    Output("stored-sku-configs", "data"),
    Input("add-sku-button", "n_clicks"),
    Input({"type": "sku-delete", "index": ALL}, "n_clicks"),
    Input({"type": "sku-rop", "index": ALL}, "value"),
    Input({"type": "sku-eoq", "index": ALL}, "value"),
    Input({"type": "sku-order-cost", "index": ALL}, "value"),
    Input({"type": "sku-holding-cost", "index": ALL}, "value"),
    Input({"type": "sku-inventory", "index": ALL}, "value"),
    Input({"type": "sku-mean-demand", "index": ALL}, "value"),
    Input({"type": "sku-std-demand", "index": ALL}, "value"),
    Input({"type": "sku-mean-split", "index": ALL}, "value"),
    Input({"type": "sku-std-split", "index": ALL}, "value"),
    Input({"type": "sku-delivery-func", "index": ALL}, "value"),
    State("stored-sku-configs", "data"),
    prevent_initial_call=True
)
def manage_skus(
    add_clicks,
    delete_clicks,
    rop_values,
    eoq_values,
    order_cost_values,
    holding_cost_values,
    inventory_values,
    mean_demand_values,
    std_demand_values,
    mean_split_values,
    std_split_values,
    delivery_func_values,
    sku_list
):
    if sku_list is None:
        sku_list = []

    triggered = ctx.triggered_id

    # Handle add SKU
    if triggered == "add-sku-button":
        new_id = max([sku['id'] for sku in sku_list], default=-1) + 1
        new_sku = {
            "id": new_id,
            "rop": 500,
            "eoq": 0,
            "z_score": 1.65,
            "order_base_cost": 50,
            "holding_cost": 1,
            "inventory": 500,
            'mean_daily_demand' : 50,
            'std_daily_demand' : 1,
            'delivery_split_centre' : 0,
            'delivery_split_std' : 0,
            "delivery_func": "constant",
            "kpi": "order_completion",
            "verbose": True
        }
        sku_list.append(new_sku)
        return sku_list

    # Handle delete SKU
    elif isinstance(triggered, dict) and triggered.get('type') == 'sku-delete':
        delete_id = triggered.get('index')
        sku_list = [sku for sku in sku_list if sku['id'] != delete_id]
        return sku_list

    else:
        for i, sku in enumerate(sku_list):
            if i < len(rop_values):
                sku['rop'] = rop_values[i]
            if i < len(eoq_values):
                sku['eoq'] = eoq_values[i]
            if i < len(order_cost_values):
                sku['order_base_cost'] = order_cost_values[i]
            if i < len(holding_cost_values):
                sku['holding_cost'] = holding_cost_values[i]
            if i < len(inventory_values):
                sku['inventory'] = inventory_values[i]
            if i < len(mean_demand_values):
                sku['mean_daily_demand'] = mean_demand_values[i]
            if i < len(std_demand_values):
                sku['std_daily_demand'] = std_demand_values[i]
            if i < len(mean_split_values):
                sku['delivery_split_centre'] = mean_split_values[i]
            if i < len(std_split_values):
                sku['delivery_split_std'] = std_split_values[i]
            if i < len(delivery_func_values):
                sku['delivery_func'] = delivery_func_values[i]
        for sku in sku_list:
            print(sku)
        return sku_list

    raise PreventUpdate

@callback(
    Output("sku-config-container", "children"),
    Input("stored-sku-configs", "data")
)
def render_sku_inputs(sku_list):
    if not sku_list:
        return html.Div("No SKUs configured yet.")
    return [render_sku_card(sku) for sku in sku_list]

def render_sku_card(sku):
    return dbc.Card(
        dbc.CardBody([
            # Card header row with title and delete button
            dbc.Row([
                dbc.Col(html.H6(f"SKU {sku['id']}", className="card-title"), width=10),
                dbc.Col(
                    dbc.Button(
                        "×",
                        id={"type": "sku-delete", "index": sku["id"]},
                        color="danger",
                        size="sm",
                        className="float-end"
                    ),
                    width=2
                )
            ], align="center"),

            # SKU parameter inputs
            dbc.Row([
                dbc.Col([
                    dbc.Label("ROP"),
                    dbc.Input(
                        id={"type": "sku-rop", "index": sku["id"]},
                        type="number",
                        value=sku["rop"],
                        min=0
                    )
                ], width=2),
                dbc.Col([
                    dbc.Label("EOQ"),
                    dbc.Input(
                        id={"type": "sku-eoq", "index": sku["id"]},
                        type="number",
                        value=sku["eoq"],
                        min=0
                    )
                ], width=2),
                dbc.Col([
                    dbc.Label("Order Cost"),
                    dbc.Input(
                        id={"type": "sku-order-cost", "index": sku["id"]},
                        type="number",
                        value=sku["order_base_cost"],
                        min=0
                    )
                ], width=2),
                dbc.Col([
                    dbc.Label("Holding Cost"),
                    dbc.Input(
                        id={"type": "sku-holding-cost", "index": sku["id"]},
                        type="number",
                        value=sku["holding_cost"],
                        min=0
                    )
                ], width=2),
                dbc.Col([
                    dbc.Label("Inventory"),
                    dbc.Input(
                        id={"type": "sku-inventory", "index": sku["id"]},
                        type="number",
                        value=sku["inventory"],
                        min=0
                    )
                ], width=2),
                dbc.Col([
                    dbc.Label("Mean Daily Demand"),
                    dbc.Input(
                        id={"type": "sku-mean-demand", "index": sku["id"]},
                        type="number",
                        value=sku["mean_daily_demand"],
                        min=0
                    )
                ], width=2),
                dbc.Col([
                    dbc.Label("Std Daily Demand"),
                    dbc.Input(
                        id={"type": "sku-std-demand", "index": sku["id"]},
                        type="number",
                        value=sku["std_daily_demand"],
                        min=0
                    )
                ], width=2),
                dbc.Col([
                    dbc.Label("Mean Splits"),
                    dbc.Input(
                        id={"type": "sku-mean-split", "index": sku["id"]},
                        type="number",
                        value=sku["delivery_split_centre"],
                        min=0
                    )
                ], width=2),
                dbc.Col([
                    dbc.Label("Std Splits"),
                    dbc.Input(
                        id={"type": "sku-std-split", "index": sku["id"]},
                        type="number",
                        value=sku["delivery_split_std"],
                        min=0
                    )
                ], width=2),
                dbc.Col([
                    dbc.Label("Delivery Function"),
                    dbc.Select(
                        id={"type": "sku-delivery-func", "index": sku["id"]},
                        options=[
                            {"label": "Constant", "value": "constant"},
                            {"label": "Quadratic", "value": "quadratic"},
                            {"label": "Logarithmic", "value": "logarithmic"}
                        ],
                        value=sku["delivery_func"]
                    )
                ], width=2)
            ], className="g-2 mt-2")
        ]),
        className="mb-3 shadow-sm"
    )

@callback(
    Output('simulation-output', 'children'),
    Output('stored-ocel', 'data'),
    Input('run-button', 'n_clicks'),
    State('stored-sku-configs', 'data'),
    State('start-date', 'date'),
    State('sim-days', 'value'),
    State('seed', 'value'),
    State('output-label', 'value'),
    prevent_initial_call=True
)
def run_simulation(n_clicks, sku_configs, start_date, days, seed, output_label):
    if not n_clicks:
        return ""


    #clear output
    try:
        shutil.rmtree(output_label)
    except OSError as e:
        print("Error: %s - %s." % (e.filename, e.strerror))
    os.makedirs(output_label)
   
    if not sku_configs:
        return html.P("No SKU configs provided."), None

    # Map string delivery funcs to actual lambdas
    for sku in sku_configs:
        print(sku)
        sku["delivery_func"] = delivery_functions[sku["delivery_func"]]

    warehouse = Warehouse(sku_configs)

    # Build config
    sim_config = {
        'warehouse' : warehouse,
        'start_date': datetime.fromisoformat(start_date),
        'days': days,
        'seed': seed,
        'output': output_label
    }


    simulation = Simulation( config=sim_config)
    simulation.run()
    global_results = simulation.evaluate_globally(report=True)
    global_table = results_table(global_results, "Global Simulation Results")
    sku_tables = []
    for sku in warehouse.SKUs.keys():
        sku_results = simulation.evaluate_skus(sku, report=True)
        sku_tables.append(results_table(sku_results, f"SKU {sku} Results"))    

    children_layout = html.Div([
        html.H4("Simulation Completed", className="mb-4"),
        global_table,
        html.Hr(),
        html.Div(sku_tables)
    ])

    return children_layout, get_ocel(f'{output_label}/')

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

    return ocel.to_json(date_format='iso', orient='split')

def results_table(data_dict, title):
        table_header = [html.Thead(html.Tr([html.Th("Metric"), html.Th("Value")]))]
        rows = []
        for key, value in data_dict.items():
            if isinstance(value, float):
                value = f"{value:.2f}"
                print(key)
            rows.append(html.Tr([html.Td(str(key).replace('_', ' ').title()), html.Td(value)]))
        table_body = [html.Tbody(rows)]
        return dbc.Card(
            dbc.CardBody([
                html.H5(title, className="card-title"),
                dbc.Table(table_header + table_body, bordered=True, striped=True, hover=True, size="sm")
            ]),
            className="mb-3"
        )