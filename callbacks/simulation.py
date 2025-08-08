from dash import Input, Output, State, callback, html
from datetime import datetime
import os, shutil
import json
import pm4py
from simulation.warehouse import Warehouse
from simulation.simulation import Simulation

delivery_functions = {
    '1 (constant)': lambda x: 1,
    'x^2': lambda x: x**2,
    '-log(x)': lambda x: -np.log(x)
}

@callback(
    Output('simulation-output', 'children'),
    Output('stored-ocel', 'data'),
    Input('run-button', 'n_clicks'),
    State('start-date', 'date'),
    State('sim-days', 'value'),
    State('seed', 'value'),
    State('mean-demand', 'value'),
    State('std-demand', 'value'),
    State('delivery-func', 'value'),
    State('mean-split', 'value'),
    State('std-split', 'value'),
    State('output-label', 'value'),
    prevent_initial_call=True
)
def run_simulation(n_clicks, start_date, days, seed, mean_demand, std_demand, delivery_func_label, mean_split, std_split, output_label):
    if not n_clicks:
        return ""

    #clear output
    try:
        shutil.rmtree(output_label)
    except OSError as e:
        print("Error: %s - %s." % (e.filename, e.strerror))
    os.makedirs(output_label)
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
        'delivery_split_centre': mean_split,
        'delivery_split_std': std_split,
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
        get_ocel(f'{output_label}/')
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

    return ocel.to_json(date_format='iso', orient='split')