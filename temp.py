import dash_core_components as dcc
import dash_html_components as html
from dash import callback_context
import dash_table
import pandas as pd
import numpy as np
import dash_bootstrap_components as dbc
import dash


app = dash.Dash(__name__)


tblcols=[{"label": "id", "id": "id"},
    {"label": "x", "id": "x"},
        {"label": "y", "id": "y"}]

df_table = pd.DataFrame([{'id': 'id_0', 'x': 0, 'y': 0}], columns=[col['label'] for col in tblcols])



def getData(id):
    n = np.random.random(1)[0]
    return {'id':f'id_{id}', 'x': n, 'y': n}
    
app.layout = html.Div([
      html.H4('Dashboard'),
      html.Button('Add Row', id='add-btn', n_clicks=0),
      dcc.Interval('table-update', interval=1_000, n_intervals = 0),
      dash_table.DataTable(
          id='table',
          data= df_table.to_dict('records'), 
          columns=tblcols
      )
])

@app.callback(
        dash.dependencies.Output('table','data'),
        [dash.dependencies.Input('table-update', 'n_intervals')])
def updateTable(n):
    global df_table
    for id in range(len(df_table)):
        n = np.random.random(1)[0]
        df_table.loc[df_table['id'] == f'id_{id}', ['x', 'y']] = [n, n + 6]
    return df_table.to_dict('records')

@app.callback(
        dash.dependencies.Output('table','data'),
        [dash.dependencies.Input('add-btn', 'n_clicks')])
def addRow(n):
    global df_table
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    if 'add-btn' in changed_id: 
        df_table = df_table.append(getData(len(df_table)), ignore_index=True)
        return df_table.to_dict('records')

if __name__ == '__main__':
     app.run_server(debug=False)
