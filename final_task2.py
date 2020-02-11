## Leaderboard for political committees, sortable by type and amount of funding 
## given to different segments of candidates as grouped by party, office, and/or geography


import dash
from dash.dependencies import Input, Output
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import requests
import json
viewer = jupyterlab_dash.AppViewer()

def runCypherQuery(query):
    
    

    # your token
    token = "####"
    

    # build the request
    url = "https://api.codefordemocracy.org/api/graph/cypher"
    headers = {
        "Authorization": "Bearer " + token
    }

    # send request and print info
    r = requests.post(url, headers=headers, data=query)
    print(r.text)
    
    return eval(r.text)


query = """MATCH (cm: Committee)-[link:contributed_to]-(cd: Candidate)
    WHERE cm.name is not NULL and cm.cmte_pty_affiliation is not NULL and cd.cand_pty_affiliation is not NULL and cd.name is not NULL
    RETURN DISTINCT cm.name as Committee_Name, cm.cmte_pty_affiliation as Committee_Party, link.transaction_tp as Type_of_funding, SUM(link.transaction_amt) as Amt_of_Funding,
    cd.name as Candidate_Name LIMIT 25"""
    
output = runCypherQuery(query)
df = pd.DataFrame(output)

app = dash.Dash(__name__)

app.layout = html.Div([
    html.Label('Group By'),
    dcc.Checklist(
        id='grouping-checklist',
        options=[
            {'label': 'Party', 'value': 0},
            {'label': 'Office', 'value': 1},
            {'label': 'Geography', 'value': 2}
        ],
        value=[]
    ),
    dash_table.DataTable(
        id='datatable-interactivity',
        columns=[
            {"name": i, "id": i,"selectable": True} for i in df.columns
        ],
        data=df.to_dict('records'),
        filter_action="native",
        sort_action="native",
        sort_mode="multi",
        row_deletable=False,
        selected_columns=[],
        page_action="native",
        page_current= 0,
        page_size= 20,
    ),
    html.Div(id='datatable-interactivity-container')
])

@app.callback(
    [Output('datatable-interactivity', 'data'),
     Output('datatable-interactivity', 'columns')],
    [Input('grouping-checklist', 'value')]
)
def update_dataframe(value):
    
    print(value)
    group_condition = [', cd.cand_pty_affiliation as Candidate_Party',\
                   ', cd.cand_office as Office',\
                   ', cd.cand_office_st as Office_State, cd.cand_office_district as Office_District']

    condition = "".join([group_condition[i] for i in value])

#     condition = ""
    query = """MATCH (cm: Committee)-[link:contributed_to]-(cd: Candidate)
    WHERE cm.name is not NULL and cm.cmte_pty_affiliation is not NULL and cd.cand_pty_affiliation is not NULL and cd.name is not NULL
    RETURN DISTINCT cm.name as Committee_Name, cm.cmte_pty_affiliation as Committee_Party, link.transaction_tp as Type_of_funding, SUM(link.transaction_amt) as Amt_of_Funding,
    cd.name as Candidate_Name
    {} LIMIT 25""".format(condition)
    
    output = runCypherQuery(query)
    df = pd.DataFrame(output)
    
    columns = [
            {"name": i, "id": i,"selectable": True} for i in df.columns
        ]
    return df.to_dict('records'), columns


@app.callback(
    Output('datatable-interactivity', 'style_data_conditional'),
    [Input('datatable-interactivity', 'selected_columns')]
)
def update_styles(selected_columns):
    return [{
        'if': { 'column_id': i },
        'background_color': '#D2F3FF'
    } for i in selected_columns]

@app.callback(
    Output('datatable-interactivity-container', "children"),
    [Input('datatable-interactivity', "derived_virtual_data"),
     Input('datatable-interactivity', "derived_virtual_selected_rows")])
def update_graphs(rows, derived_virtual_selected_rows):
    
    if derived_virtual_selected_rows is None:
        derived_virtual_selected_rows = []

    dff = df if rows is None else pd.DataFrame(rows)

    colors = ['#7FDBFF' if i in derived_virtual_selected_rows else '#0074D9'
              for i in range(len(dff))]


viewer.show(app)