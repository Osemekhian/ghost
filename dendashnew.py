#pip install dash
#pip install dash-renderer
#pip install dash-html-components
#pip install dash-core-components
#pip install plotly --upgrade

import dash as dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly.express as px
from datetime import date
import random
style={'textAlign':'center'}
steps=0.1
marks= lambda min,max:{i:f"{i}" for i in range(min,max)}
#===========================================
def datum():
    return pd.read_csv(
        'https://docs.google.com/spreadsheets/d/e/2PACX-1vTiQBygf4Uo45gGW4qfdO5ekeyYSz6O9JP9SkBogtLSzlGrE5bMa0pJy2voQakRf_izgZwzU3WwVaA_/pub?gid=593030798&single=true&output=csv')

my_app= dash.Dash(__name__,external_stylesheets=[dbc.themes.SOLAR]) #dbc.themes.MORPH
server= my_app.server
my_app.layout = html.Div([
    html.H1("Denny's DashBoard"),html.Br(),
    dcc.RadioItems(id='radio1',
                                   options=[{"label": "Compare", "value": "Compare"},
                                            {"label": "Seperate", "value": "Seperate"}],
                                   value='Seperate', labelStyle={'display': 'block'}),
    html.P('Store:'),
    dcc.Dropdown(id='drop1',
                 options=[{'label': i, 'value': i} for i in ['Benning Road','Bladensburg']],
                 multi=False,
                 value="Benning Road",placeholder='Select Store...'), html.Br(),
    html.P('Date:'),
    dcc.DatePickerSingle(
        id='my-date-picker-single',
        min_date_allowed=date(2023, 1, 1),
        max_date_allowed=date(2030, 1, 1),
        initial_visible_month=date(2023, 1, 4),
        date=date.today()), #date(2023, 1, 4)),
    html.Div(id='out'),
    html.Div(html.P(f'Bravelion {date.today()}'),style={'textAlign': 'center'})
],style=style)

@my_app.callback(
    Output('out', 'children'),
    [Input('my-date-picker-single', 'date'),
     Input('drop1', 'value'),
     Input('radio1','value')])
def update(a,b,c):
    df= datum()
    # df = pd.read_csv(
    #     'https://docs.google.com/spreadsheets/d/e/2PACX-1vTiQBygf4Uo45gGW4qfdO5ekeyYSz6O9JP9SkBogtLSzlGrE5bMa0pJy2voQakRf_izgZwzU3WwVaA_/pub?gid=593030798&single=true&output=csv')
    date_object = date.fromisoformat(a)
    date_string = date_object.strftime('%#m/%#d/%Y')
    filter = df[df.Date == date_string]
    filter = filter[filter.Store == b]
    if len(filter)==0:
        return html.P("No Feedback :( Try again!")
    fig = px.bar(filter,
                  x='Time',
                  y='Sales',text_auto=True,
                 title=f"{b} Sales")
    fig2 = px.bar(filter,
                  x='Time',
                  y=['Total Labor'],text_auto=True,
                  title=f"{b} Labor")
    fig3 = px.bar(filter,
                 x='Time',
                 y='All Employees', text_auto=True,
                 title=f"{b} Employees")

    if c == "Seperate":
        return html.Div([dcc.Graph(figure=fig),html.Br(),
                         dcc.Graph(figure=fig2),html.Br(),
                         dcc.Graph(figure=fig3), html.Br()
                         ])
    else:
        fig_compare = px.bar(df,
                             x='Time',
                             y='Sales', text_auto=True,
                             color='Store', title='Sales Between Stores')
        fig_compare2 = px.bar(df,
                              x='Time',
                              y=['Total Labor'], text_auto=True, color='Store',
                              title='Labor Between Stores')
        fig_compare3 = px.bar(df,
                              x='Time',
                              y='All Employees', text_auto=True,color='Store',
                              title='Employees Between Stores')

        return html.Div([dcc.Graph(figure=fig_compare),html.Br(),
                         dcc.Graph(figure=fig_compare2),html.Br(),
                         dcc.Graph(figure=fig_compare3), html.Br()
                         ])

if __name__ == '__main__':
    my_app.run_server(
        debug=False
    )


