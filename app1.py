import dash
from dash.dependencies import Input, Output
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import requests
import json

def runCypherQuery(query):
    
    

    # your token
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJuYXRtZW5vbkBzZWFzLnVwZW5uLmVkdSIsImp0aSI6ImViMjdiOGE4LTI5NzYtNGM5Yy1iODQ2LWEyNThiYmRjMjk1NSIsImV4cCI6MTU4MjU2NDk5OSwiaXNzIjoiaHR0cDovL215Y29kZWNhbXAuaW8iLCJhdWQiOiJodHRwOi8vbXljb2RlY2FtcC5pbyJ9.br37j37T28nXV06jinqZKcivu2icNcdj_gp3Yoo07h0"
    

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
    RETURN DISTINCT cm.name, cm.cmte_pty_affiliation, link.transaction_tp as type_of_funding, SUM(link.transaction_amt) as funding,
    cd.name LIMIT 25"""
    
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
    Output('datatable-interactivity', 'data'),
    [Input('grouping-checklist', 'value')]
)
def update_dataframe(value):
    
    print(value)
    group_condition = [', cd.cand_pty_affiliation',\
                   ', cd.cand_office',\
                   ', cd.cand_office_st, cd.cand_office_district']

    condition = "" + "".join([group_condition[i] for i in value])

#     condition = ""
    query = """MATCH (cm: Committee)-[link:contributed_to]-(cd: Candidate)
    WHERE cm.name is not NULL and cm.cmte_pty_affiliation is not NULL and cd.cand_pty_affiliation is not NULL and cd.name is not NULL
    RETURN DISTINCT cm.name, cm.cmte_pty_affiliation, link.transaction_tp as type_of_funding, SUM(link.transaction_amt) as funding,
    cd.name
    {} LIMIT 25""".format(condition)
    
    output = runCypherQuery(query)
    df = pd.DataFrame(output)
    return df.to_dict('records')


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