import dash as dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import pandas_datareader as web
from pandas_datareader import data
from datetime import date
import random, datetime
import yfinance as yf
yf.pdr_override()
style={'textAlign':'center'}
steps=0.1
marks= lambda min,max:{i:f"{i}" for i in range(min,max)}
#===========================================
sym= pd.read_csv('https://raw.githubusercontent.com/Bravelion2017/Machine-Learning/main/stock_crypto_symbols.csv').iloc[:,1:]
sym= dict(zip(sym.Name,sym.Symbol))

# st= pd.read_csv("C:/Users/oseme/Documents/stocks_list.txt",header=None)
columns = ['High','Low','Open','Close','Volume','Adj Close']

def stock_df(start,end,symbols):
    df=data.get_data_yahoo(symbols,start=start,end=end)
    return df

#===========================================
my_app= dash.Dash(__name__,external_stylesheets=[dbc.themes.SOLAR]) #dbc.themes.MORPH
server= my_app.server
my_app.layout = html.Div([
    html.H1("Stocks/Crypto Price Dashboard"),
    html.H6("By: Osemekhian Ehilen | Data Source: Yahoo API"), html.Br(),

    html.P('Stock/Crypto Symbol:'),
    dcc.Dropdown(id='drop1',
                 options=[{'label': i, 'value': j} for i,j in sym.items()],
                 multi=False,
                 value="AAPL",placeholder='Select company...'), html.Br(),
    # dcc.Input(id='in',type='text',placeholder='Specific symbol-e.g IBM'),
    html.P('(Note: If no update on chart, click the stock/crypto symbol again)'),
    html.Br(),

    html.P('Indices:'),
    dcc.Dropdown(id='drop2',
                 options=[{'label': i, 'value': i} for i in columns],
                 multi=False,clearable=False,
                 value="Close"), html.Br(),
    html.P("Date Range:"),
    dcc.DatePickerRange(id='start',
                        min_date_allowed=date(2000,1,1),
                        max_date_allowed=str(date.today()),
                        start_date=str(date(2017,1,1)),
                        end_date=date.today()
                        ), html.Br(),
# Line chart
    html.H2('Price Chart'),
    html.Div(id='out'), html.Br(),

# Candle stick chart
    html.Br(),
    html.H2('Price Candles'),
    html.P('Stock Market:'),
    # dcc.Dropdown(id='drop3',
    #              options=[{'label': i, 'value': j} for i,j in sym.items()],
    #              multi=False,
    #              value="AAPL",placeholder='Select company...'),
    dcc.Checklist(
        id='check1',
        options=[{'label': 'Include Rangeslider',
                  'value': 'slider'}],
        value=['slider']
    ),

    html.Div(id='out2'),
    html.Br(),

    html.P('Specific Price'),
    dcc.DatePickerSingle(id='start1',
                        min_date_allowed=date(2000,1,1),
                        max_date_allowed=str(date.today()),
                        date=str(date.today()-datetime.timedelta(days=1))
                        ),
    html.P('Indices:'),
    html.Div([dcc.Dropdown(id='drop22',
                 options=[{'label': i, 'value': i} for i in columns],
                 multi=False,clearable=False,
                 value="Close")],style={'width': '20%','display': 'inline-block'}),
    html.Div(id='singleout',style={'textAlign':'center'}),
    dcc.Store(id='store1'),
    html.P('Bravelion® 2024',dir='rtl')

],style=style)

@my_app.callback([
    Output('out','children'),Output('store1','data')
    ],
    [Input('drop1','value'),
     Input('drop2','value'),
     Input('start', 'start_date'),
     Input('start', 'end_date')
     ]
)
def update(col1,col2,a,z):
    df = stock_df(a,z,symbols=col1)
    filtr= df[col2] #df[col2][col1[:]]
    fig = px.line(
        filtr,x=filtr.index,y=filtr,template="plotly_dark",
        title=f'{col1} {col2}'
    )

    return dcc.Graph(figure=fig), df.T.to_json(orient='table')

@my_app.callback(
    Output('out2','children'),
    [Input('drop1','value'),
     Input('start', 'start_date'),
     Input('start', 'end_date'),
     Input('check1','value'),
     Input('store1', 'data')]
)
def update(col1,a,z,check,store):
    df = stock_df(a, z, symbols=col1)
    # df= pd.read_json(store,orient='table').T
    # df.index=  pd.to_datetime(df.index.str.split('T').str[0],format='%Y-%m-%d')
    fig = go.Figure(data=[go.Candlestick(x=df['Open'].index,
                    open=df['Open'], high=df['High'],
                    low=df['Low'], close=df['Close'])
                          ])

    fig.update_layout(
        xaxis_rangeslider_visible='slider' in check,
        template = "plotly_dark",
        title=f'{col1} Candle Stick Chart' #changed col1 from s
    )
    return dcc.Graph(figure=fig)

@my_app.callback(
    Output('singleout','children'),
    [Input('drop1','value'),
     Inpu('drop22','value'),
     Input('start1','date'),
     Input('start', 'start_date'),
     Input('start', 'end_date'),
     Input('store1', 'data')
     ]
)
def update(col1,b,c,y,z,store):
    df = stock_df(y, z, symbols=col1)
    # df = pd.read_json(store, orient='table').T
    # df.index = pd.to_datetime(df.index.str.split('T').str[0], format='%Y-%m-%d')
    try:
        dat= df[b].loc[c] #df[b][a].loc[c]
        return round(dat,5)
    except:
        return f"Oops! No Result"





if __name__ == '__main__':
    my_app.run_server(
        debug=True,
        port=8080
        host="0.0.0.0",
    )
