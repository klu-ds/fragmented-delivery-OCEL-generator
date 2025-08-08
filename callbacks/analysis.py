from dash import callback, Output, Input, State, html, dcc, dash_table, get_asset_url
import pandas as pd
import pm4py
import plotly.express as px
import networkx as nx
import plotly.graph_objects as go
import dash_cytoscape as cyto 
import tqdm

@callback(
    Output('ocel-table-container', 'children'),
    Output('ocel-stats-container', 'children'),
#    Output('pm-variant-plot', 'children'),
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
    
    # # Use pm4py to get variants dataframe for process mining plot
    # try:
    #     # convert ocel_df back to OCEL object for pm4py (you may need to read from json)
    #     # if you have a pm4py OCEL object you can do:
    #     ocel_obj = pm4py.read_ocel2_json("OCEL.json")  # or adapt if stored differently
        
    #     # ocdfg = pm4py.discover_ocdfg(ocel_obj)
    #     # # Simple bar chart of top variants by frequency
    #     # pm4py.vis.save_vis_ocdfg(ocdfg=ocdfg,file_path="assets/ocdfg.png")
    #     # ocdfg_img = html.Img(src=get_asset_url("ocdfg.png"))

    #     ocdfg = pm4py.discover_ocdfg(ocel_obj)
    #     G = pm4py.convert_ocel_to_networkx(ocel_obj)
    #     # fig = plot_ocdfg_graph(G)
    #     # ocdfg_graph = dcc.Graph(figure=fig)

    #     elements = convert_networkx_to_dash_cytoscape(G)

    #     cyto = cyto.Cytoscape(
    #         id='cytoscape-ocel-network',
    #         elements=elements,
    #         layout={'name': 'cose'},  # other options: 'circle', 'breadthfirst'
    #         style={'width': '100%', 'height': '600px'},
    #         stylesheet=[
    #             {'selector': 'node', 'style': {'label': 'data(label)', 'font-size': '10px'}},
    #             {'selector': 'edge', 'style': {
    #                 'curve-style': 'bezier',
    #                 'target-arrow-shape': 'triangle',
    #                 'line-color': '#888',
    #                 'target-arrow-color': '#888'
    #             }}
    #         ]
    #     )
    # except Exception as e:
    #     plot = html.P(f"Could not generate variant plot: {e}")
    
    return table, stats

def convert_networkx_to_dash_cytoscape(G):
    pos = nx.spring_layout(G, k=0.3, iterations=50, seed=42)  # adjust parameters for better spacing

    elements = []

    # Add nodes with positions and labels
    for node_id in G.nodes:
        node_data = G.nodes[node_id]
        try:
            label = node['data']['attr']['ocel:activity']
        except Exception as e:
            label = node_data.get("label", str(node_id))
        x, y = pos[node_id]

        elements.append({
            'data': {'id': str(node_id), 'label': label},
            'position': {'x': x * 1000, 'y': y * 1000},  # scale for better layout in UI
        })

    # Add edges
    for source, target in G.edges:
        edge_data = G.edges[source, target]
        elements.append({
            'data': {
                'source': str(source),
                'target': str(target),
                'label': edge_data.get("label", "")
            }
        })

    return elements

    # cyjs = nx.cytoscape_data(G)
    # nodes = cyjs["elements"]["nodes"]
    # edges = cyjs["elements"]["edges"]

    # # Optionally set label for each node
    # for node in nodes:
    #     try:
    #         #node["data"]["label"] = node["data"].get("name", node["data"]["id"])
    #         node["data"]["label"] = node['data']['attr']['ocel:activity']
    #     except Exception as e:
    #         node["data"]["label"] = node["data"].get("name", node["data"]["id"])
    # return nodes + edges

@callback(
    Output("ocel-network-container", "children"),
    Input("show-ocel-network", "n_clicks"),
    State("stored-ocel", "data"),
    prevent_initial_call=True
)
def display_ocel_network(n_clicks, ocel_json):
    if not ocel_json:
        return html.P("No OCEL data available.")

    try:
        # Deserialize OCEL
        ocel_df = pm4py.read_ocel2_json("OCEL.json")
        G = pm4py.convert_ocel_to_networkx(ocel_df)

        elements = convert_networkx_to_dash_cytoscape(G)

        return cyto.Cytoscape(
                    id='cytoscape-ocel-network',
                    elements=convert_networkx_to_dash_cytoscape(G),
                    layout={'name': 'preset'},  # use preset to preserve spring layout
                    style={'width': '100%', 'height': '600px'},
                    stylesheet=[
                        {'selector': 'node', 'style': {
                            'label': 'data(label)',
                            'font-size': '10px',
                            'background-color': '#0074D9',
                            'color': '#000'
                        }},
                        {'selector': 'edge', 'style': {
                            'curve-style': 'bezier',
                            'target-arrow-shape': 'triangle',
                            'line-color': '#888',
                            'target-arrow-color': '#888',
                            'width': 1
                        }}
                    ]
                )
    except Exception as e:
        return html.P(f"Error generating graph: {str(e)}")