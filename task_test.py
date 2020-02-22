#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import dash
import jupyterlab_dash
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


query = """MATCH (a: Source)-[l1: associated_with]-(e:Entity)-[l2: associated_with]-(t:Tweeter)
WHERE a.bias_score is not NULL and t.name <> ""
RETURN DISTINCT t.name as name, a.bias_score as bias_score, a.conspiracy_flag as conspiracy_flag,a.factually_questionable_flag as factually_questionable_flag,
a.propaganda_flag as propaganda_flag, a.hate_group_flag as hate_group_flag,a.satire_flag as satire_flag
LIMIT 10
"""
    
output = runCypherQuery(query)
df = pd.DataFrame(output)

app = dash.Dash(__name__)

bar_plot_layout = {
                'xaxis': {'automargin': True,
                         'title': {"text": 'Twitter Users'}
                         },
                'yaxis': {'automargin': True,
                         'title': {"text": 'Variables'}
                         },
                'title': 'Dash Data Visualization',
                
            }




app.layout = html.Div(children=[
    html.H1(children='Code For Democracy'),

    html.H2(children='''
        Analyzing Twitter Flags
    '''),
    html.H3('What should the data be sorted by?'),
    dcc.Checklist(
        id='sorting_checklist',
        options=[
            {'label': 'Bias Score', 'value': 0},
            {'label': 'Conspiracy Flag', 'value': 1},
            {'label': 'Factually Questionable Flag', 'value': 2},
            {'label': 'Propaganda Flag', 'value':3},
            {'label': 'Hate Group Flag', 'value':4},
            {'label': 'Satire Flag', 'value':5}
        ],
        value=[]
    ),
    html.H3('What would you like to display?'),
    dcc.Checklist(
        id='display_checklist',
        options=[
            {'label': 'Bias Score', 'value': 0},
            {'label': 'Conspiracy Flag', 'value': 1},
            {'label': 'Factually Questionable Flag', 'value': 2},
            {'label': 'Propaganda Flag', 'value':3},
            {'label': 'Hate Group Flag', 'value':4},
            {'label': 'Satire Flag', 'value':5}
        ],
        value=[0,1,2,3,4,5]
    ),
    html.H3('How many Twitter users would you like to display?'),
    dcc.Dropdown(
        id='show_num',
        options=[
            {'label': '5', 'value': 5},
            {'label': '10', 'value': 10},
            {'label': '15', 'value': 15},
            {'label': '20', 'value':20},
            {'label': '25', 'value':25}
        ],
        value=10
    ),

    dcc.Graph(
        id='example-graph',
        figure={
            'data': [
                
                {'x': df['name'], 'y': df['bias_score'], 'type': 'bar'},
                {'x': df['name'], 'y': df['conspiracy_flag'], 'type': 'bar'},
                {'x': df['name'], 'y': df['factually_questionable_flag'], 'type': 'bar'},
                {'x': df['name'], 'y': df['propaganda_flag'], 'type': 'bar'},
                {'x': df['name'], 'y': df['hate_group_flag'], 'type': 'bar'},
                {'x': df['name'], 'y': df['satire_flag'], 'type': 'bar'}
            ],
            'layout': bar_plot_layout,
        }
    )
])
# @app.callback(
#     Output('example-graph','figure'),
#     [Input('grouping-checklist', 'value')]
# )
# def update_barplot_groupby(value):
    
@app.callback(Output('example-graph','figure'),              [Input('sorting_checklist','value'),Input('display_checklist', 'value'),Input('show_num','value')])
def update_barplot(sortvalue, displayvalue, showvalue):
    
    sort_cond = [' a.bias_score DESC',                   ' a.conspiracy_flag DESC',                   ' a.factually_questionable_flag DESC', ' a.propaganda_flag DESC', ' a.hate_group_flag DESC', ' a.satire_flag DESC' ]
    display_cond = [', a.bias_score as bias_score',                   ', a.conspiracy_flag as conspiracy_flag',                   ', a.factually_questionable_flag as factually_questionable_flag',                   ', a.propaganda_flag as propaganda_flag',                   ', a.hate_group_flag as hate_group_flag',                   ', a.satire_flag as satire_flag'
                   ]
    
    output=[]
    condition2=''
    if len(displayvalue)!=0:
        condition=''
        if len(sortvalue)!=0:
            condition = "ORDER BY " + ",".join([sort_cond[i] for i in sortvalue])
        condition2 = "RETURN DISTINCT t.name as name" + "".join([display_cond[i] for i in displayvalue])
        query = """MATCH (a: Source)-[l1: associated_with]-(e:Entity)-[l2: associated_with]-(t:Tweeter) WHERE a.bias_score is not NULL and t.name <> "" {} {} LIMIT {}""".format(condition2,condition, showvalue)
    
        output = runCypherQuery(query)
        if len(output) != 0:
            df = pd.DataFrame(output)
            dispdata=[]
            if 0 in displayvalue:
                dispdata.append({'x': df['name'], 'y': df['bias_score'], 'type': 'bar', 'name':'Bias Score'})
            if 1 in displayvalue:
                dispdata.append({'x': df['name'], 'y': df['conspiracy_flag'], 'type': 'bar', 'name':'Conspiracy Flag'})
            if 2 in displayvalue:
                dispdata.append({'x': df['name'], 'y': df['factually_questionable_flag'], 'type': 'bar','name':'Factually Questionable Flag'})
            if 3 in displayvalue:
                dispdata.append({'x': df['name'], 'y': df['propaganda_flag'], 'type': 'bar','name':'Propaganda Flag'})
            if 4 in displayvalue:
                dispdata.append({'x': df['name'], 'y': df['hate_group_flag'], 'type': 'bar','name':'Hate Group Flag'})
            if 5 in displayvalue:
                dispdata.append({'x': df['name'], 'y': df['satire_flag'], 'type': 'bar','name':'Satire Flag'})
            return {'data': dispdata,
                'layout': bar_plot_layout,
                    }
        
            
        
    return {}

# @app.callback(
#     [Output('datatable-interactivity', 'data'),
#      Output('datatable-interactivity', 'columns')],
#     [Input('grouping-checklist', 'value')]
# )
# def update_dataframe(value):
    
#     print(value)
#     group_condition = [', cd.cand_pty_affiliation as Candidate_Party',\
#                    ', cd.cand_office as Office',\
#                    ', cd.cand_office_st as Office_State, cd.cand_office_district as Office_District']

#     condition = "".join([group_condition[i] for i in value])

# #     condition = ""
#     query = """MATCH (cm: Committee)-[link:contributed_to]-(cd: Candidate)
#     WHERE cm.name is not NULL and cm.cmte_pty_affiliation is not NULL and cd.cand_pty_affiliation is not NULL and cd.name is not NULL
#     RETURN DISTINCT cm.name as Committee_Name, cm.cmte_pty_affiliation as Committee_Party, link.transaction_tp as Type_of_funding, SUM(link.transaction_amt) as Amt_of_Funding,
#     cd.name as Candidate_Name
#     {} LIMIT 25""".format(condition)
    
#     output = runCypherQuery(query)
#     df = pd.DataFrame(output)
    
#     columns = [
#             {"name": i, "id": i,"selectable": True} for i in df.columns
#         ]
#     return df.to_dict('records'), columns


# @app.callback(
#     Output('datatable-interactivity', 'style_data_conditional'),
#     [Input('datatable-interactivity', 'selected_columns')]
# )
# def update_styles(selected_columns):
#     return [{
#         'if': { 'column_id': i },
#         'background_color': '#D2F3FF'
#     } for i in selected_columns]

# @app.callback(
#     Output('datatable-interactivity-container', "children"),
#     [Input('datatable-interactivity', "derived_virtual_data"),
#      Input('datatable-interactivity', "derived_virtual_selected_rows")])
# def update_graphs(rows, derived_virtual_selected_rows):
    
#     if derived_virtual_selected_rows is None:
#         derived_virtual_selected_rows = []

#     dff = df if rows is None else pd.DataFrame(rows)

#     colors = ['#7FDBFF' if i in derived_virtual_selected_rows else '#0074D9'
#               for i in range(len(dff))]

if __name__ == '__main__':
    app.run_server(debug=True)

