## Leaderboard for Twitter users, sortable by the bias rating and 
## flags of the news sources they tend to link to


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

query = """MATCH (a: Source)-[l1: associated_with]-(e:Entity)-[l2: associated_with]-(t:Tweeter)
WHERE a.bias_score is not NULL and t.name <> ""
RETURN DISTINCT t.name as name, a.bias_score as bias_score, a.conspiracy_flag as conspiracy_flag,a.factually_questionable_flag as factually_questionable_flag,
a.propaganda_flag as propaganda_flag, a.hate_group_flag as hate_group_flag,a.satire_flag as satire_flag

"""
#ORDER BY a.conspiracy_flag DESC, a.bias_score DESC
#LIMIT 25
output = runCypherQuery(query)

result = {str(i):row for i,row in enumerate(output)}

with open('result.json', 'w') as fp:
    json.dump(result, fp)

df = pd.read_json('result.json').transpose()

cols = ['name', 'bias_score', 'conspiracy_flag','factually_questionable_flag','propaganda_flag','hate_group_flag','satire_flag']

df = df[cols]

print(df)

app = dash.Dash(__name__)

app.layout = html.Div([
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
    # When the table is first rendered, `derived_virtual_data` and
    # `derived_virtual_selected_rows` will be `None`. This is due to an
    # idiosyncracy in Dash (unsupplied properties are always None and Dash
    # calls the dependent callbacks when the component is first rendered).
    # So, if `rows` is `None`, then the component was just rendered
    # and its value will be the same as the component's dataframe.
    # Instead of setting `None` in here, you could also set
    # `derived_virtual_data=df.to_rows('dict')` when you initialize
    # the component.
    if derived_virtual_selected_rows is None:
        derived_virtual_selected_rows = []

    dff = df if rows is None else pd.DataFrame(rows)

    colors = ['#7FDBFF' if i in derived_virtual_selected_rows else '#0074D9'
              for i in range(len(dff))]

    '''return [
        dcc.Graph(
            id=column,
            figure={
                "data": [
                    {
                        "x": dff["country"],
                        "y": dff[column],
                        "type": "bar",
                        "marker": {"color": colors},
                    }
                ],
                "layout": {
                    "xaxis": {"automargin": True},
                    "yaxis": {
                        "automargin": True,
                        "title": {"text": column}
                    },
                    "height": 250,
                    "margin": {"t": 10, "l": 10, "r": 10},
                },
            },
        )
        # check if column exists - user may have deleted it
        # If `column.deletable=False`, then you don't
        # need to do this check.
        for column in ["pop", "lifeExp", "gdpPercap"] if column in dff
    ]'''


viewer.show(app)