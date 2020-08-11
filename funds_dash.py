# creates a dash (html based) visualization of chosen funds growth
# 

import json
import pandas as pd
import numpy as np

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State


# import funds_rates dict and number of units in possesion
with open("C:\\Users\\Pawel\\Documents\\Github\\projects\\personal_invest_dash\\data\\funds_rates.json", 'r', encoding='utf-8') as f_saved:
    funds_rates = json.load(f_saved)

with open("C:\\Users\\Pawel\\Documents\\Github\\projects\\personal_invest_dash\\data\\P_units.json", 'r', encoding='utf-8') as f:
    P_units = json.load(f)


# some key names are parts of other key names, therefore, I cannot use 'a in b' cause it might give me same element multiple times,
# instead I remove parts of key names after '(' and use 'a == b'
funds_rates2 = {}
for key in funds_rates:
    new_key = key.split("(")[0].strip()
    funds_rates2[new_key] = funds_rates[key]

# get values of how much money units are worth
dict1 = {}
for i in P_units:
    for j in funds_rates2:
        if i == j:
            dict2 = {}
            for k in funds_rates2[j]:
                dict2[k] = P_units[i]*funds_rates2[j][k]
            dict1[j] = dict2

df = pd.DataFrame(dict1)
df = df.sort_index(axis = 0)

# fill empty cells in dataFrame by interpolated values
df_interp = (df.interpolate(method='linear')).interpolate(method='linear', limit_direction='backward')
# sum of all my funds
df_sum = df_interp.sum(axis = 1)

# check which date has all the values filled
def first_last_full(data_frame, first_last):
    # check the first/last row of dataframe that is fully filled and return its index
    # inputs: (dataFrame, first/last = +1/-1)
    if first_last == -1:
        idx = -1
    elif first_last == 1:
        idx = 0
    all_nan = True
    while all_nan == True:
        last_full = idx
        all_nan = pd.isna(data_frame.iloc[idx]).any()
        idx = idx + first_last
    return last_full

last_full_idx = first_last_full(df, -1)


colors = {
    'bg': '#111111',
    'bg2': '#1a1a1a',
    'text': '#A9A9A9',
    'bg-tran': 'rgba(0,0,0,0)'
    }


app = dash.Dash(__name__)

app.layout = html.Div(
    style = {'backgroundColor': colors['bg'], 
             },
    children = [
        html.Table([
        
        html.Tr([
            html.Td([
        
                html.Div([
                    
                    dcc.Dropdown(
                        id = 'drop-myfunds',
                        options = [
                            {'label': i, 'value': i} for i in df.columns
                            ],
                        multi = True,
                        value = df.columns[0]
                        ),
                    
                    html.Button('Select all', id = 'sa-button'),
                    
                    dcc.Graph(
                        id = 'plot-myfunds',
                    ),
                    
                    dcc.RangeSlider(
                        id = 'data-slider',
                        updatemode = 'mouseup',
                        min = 0,
                        max = len(df.index)-1,
                        value = [0, len(df.index)-1],
                        marks = {i: {'label': date}
                                 for i, date in enumerate(df.index)
                            }
                        )
                    ],
                    style = {
                        #'width': '48%',
                        #'padding': 10,
                        #'display': 'inline-block',
                        'backgroundColor': colors['bg2']
                        }
                    )], style = {'width': '60%', 'padding': 5}),
            
            html.Td([
        
                html.Div([
                        
                    dcc.DatePickerSingle(
                        id = 'pick-date',
                        date = df.index[last_full_idx],
                        display_format = 'DD/MM/YYYY',
                        min_date_allowed = df.index[1],
                        max_date_allowed = df.index[last_full_idx],
                        ),
                    
                    dcc.Graph(
                        id = 'my-shares',
                        ),
                ],
                style = {
                    #'width': '48%',
                    #'padding': 10,
                    #'display': 'inline-block',
                    'backgroundColor': colors['bg2']
                    }
                )
            ], style = {'padding': 5})
    ])])])

# callback for the 'select all' button
@app.callback(
    Output('drop-myfunds', 'value'),
    [Input('sa-button', 'n_clicks')],
    state=[State('drop-myfunds', 'value')])
def select_all(btn, btn2):
        return df.columns

# callback to update 'my-funds' plot based on chosen funds and time range
@app.callback(
    Output('plot-myfunds', 'figure'),
    [Input('drop-myfunds', 'value'),
     Input('data-slider', 'value')])
def update_myfunds_plot(funds, f_date):
    data = []
    for fund in funds:
        # change of the fund unit value compared to chosen initial date
        y_change = (df[fund][f_date[0]:f_date[1]+1]-df[fund][f_date[0]])/df[fund][f_date[0]]*100
        data.append(dict(
            x = df.index[f_date[0]:f_date[1]+1],
            y = np.round(y_change,2),
            name = fund,
            ))
    # change of the sum of my funds compared to chosen initial date
    y_sum_change = (df_sum[f_date[0]:f_date[1]+1]-df_sum[f_date[0]])/df_sum[f_date[0]]*100
    data.append(dict(
        x = df.index[f_date[0]:f_date[1]+1],
        y = np.round(y_sum_change,2),
        name = 'Sum',
        mode = 'lines+markers',
        line = {'width': 5, 'color': 'white'},
        ))
    return {
        'data': data,
        'layout': {
            'yaxis': {
                'title': {'text':'Change [%]'}},
            'legend': {
                'orientation': 'h'
                },
            'paper_bgcolor': colors['bg-tran'],
            'plot_bgcolor': colors['bg-tran'],
            'font':{
                'color': colors['text']}
            }
        }

# callback to update the pie chart
@app.callback(
    Output('my-shares', 'figure'), 
    [Input('pick-date', 'date')])
def update_pie(date):
    return {
            'data': [
                dict(
                    values = np.around(df.loc[date].values),
                    labels = df.columns,
                    type = 'pie',
                    hole = .3,
                    hoverinfo = 'label+value'
                    )
                ],
            'layout': {
                'legend': {'orientation': 'h'},
                'paper_bgcolor': colors['bg-tran'],
                'plot_bgcolor': colors['bg-tran'],
                'font':{
                    'color': colors['text']
                    },
                }
            }
    

if __name__ == '__main__':
    app.run_server(debug=False)