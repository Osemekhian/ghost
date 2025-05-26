# libraries import
import dash as dash
from dash import dcc,dash_table, State
import joblib, base64
from io import BytesIO
import io
from dash import html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
# from plotly.subplots import make_subplots
# from datetime import date
import random
style= {'textAlign': 'center'}
style2={'width': '80%',
        'borderWidth': '1px',
        'borderStyle': 'dashed',
        'borderRadius': '5px',
        'textAlign': 'center',
        'background-color':'#485785',
        #'color':'white',
        'align-items':'center',
        'margin':'auto'
    }
steps=0.1
random_state= 42
marks= lambda min,max:{i:f"{i}" for i in range(min,max)}

# helper function
def log_sigmoid(n):
    """
    log_sigmoid function
    :param n: summation of Wp+b
    :return: a
    """
    a = 1 / (1 + np.exp(-n))
    return a
def purelin(n):
    """
    linear function
    :param n: summation of Wp+b
    :return: a
    """
    return n
def gaussian(n):
    return np.exp(-n**2)
def b64_image(image_filename):
    with open(image_filename, 'rb') as f:
        image = f.read()
    return 'data:image/png;base64,' + base64.b64encode(image).decode('utf-8')

# The App
app= dash.Dash(__name__,external_stylesheets=[dbc.themes.SKETCHY],suppress_callback_exceptions=True) #dbc.themes.MORPH | dbc.themes.SOLAR
server= app.server
app.layout = html.Div([
    html.Br(),
    html.H2("Function Approximation"),
    html.Pre("MLP | RBF Network"),
    dcc.Tabs(id="tab1", children=[
        dcc.Tab(label="MLP",value="MLP"),
        dcc.Tab(label="RBF", value="RBF"),
    ]),
    html.Div(id="tabout"),
], style=style)

# MLP layout
p = np.linspace(-5, 5, 1000)
mlp_layout = html.Div([
    # Image and Graph row
    html.Div([
        html.Div([
            html.Img(src="https://github.com/Osemekhian/ghost/blob/main/function%20approximation%20image.png?raw=true")
        ], style={'width': '48%', 'display': 'inline-block'}),

        html.Div([
            dcc.Graph(id='graph-3')
        ], style={'width': '48%', 'display': 'inline-block', 'float': 'right'})
    ]),

    html.Br(), html.Br(), html.Br(), html.Br(),html.Br(), html.Br(),

    dbc.Row([
        dbc.Col([  # Left column for sliders (4 sliders)
            html.P('b11'),
            dcc.Slider(id='b11',
                       min=-10,
                       max=10,
                       value=1,
                       step=0.001,
                       marks={i: f"{i}" for i in range(-10, 10, 1)},
                       tooltip={"placement": "bottom", "always_visible": False}
                       ),
            # html.Br(),

            html.P('b12'),
            dcc.Slider(id='b12',
                       min=-10,
                       max=10,
                       value=1,
                       step=0.001,
                       marks={i: f"{i}" for i in range(-10, 10, 1)},
                       tooltip={"placement": "bottom", "always_visible": False}
                       ),
            # html.Br(),

            html.P('w11'),
            dcc.Slider(id='w11',
                       min=-10,
                       max=10,
                       value=1,
                       step=0.001,
                       marks={i: f"{i}" for i in range(-10, 10, 1)},
                       tooltip={"placement": "bottom", "always_visible": False}
                       ),
            #html.Br(),

            html.P('w12'),
            dcc.Slider(id='w12',
                       min=-10,
                       max=10,
                       value=1,
                       step=0.001,
                       marks={i: f"{i}" for i in range(-10, 10, 1)},
                       tooltip={"placement": "bottom", "always_visible": False}
                       ),
        ], width=6),

        dbc.Col([  # Right column for sliders (3 sliders)
            html.P('b21'),
            dcc.Slider(id='b21',
                       min=-10,
                       max=10,
                       value=1,
                       step=0.001,
                       marks={i: f"{i}" for i in range(-10, 10, 1)},
                       tooltip={"placement": "bottom", "always_visible": False}
                       ),
            #html.Br(),

            html.P('w21'),
            dcc.Slider(id='w21',
                       min=-10,
                       max=10,
                       value=1,
                       step=0.001,
                       marks={i: f"{i}" for i in range(-10, 10, 1)},
                       tooltip={"placement": "bottom", "always_visible": False}
                       ),
            #html.Br(),

            html.P('w22'),
            dcc.Slider(id='w22',
                       min=-10,
                       max=10,
                       value=1,
                       step=0.001,
                       marks={i: f"{i}" for i in range(-10, 10, 1)},
                       tooltip={"placement": "bottom", "always_visible": False}
                       ),
        ], width=6)
    ]),

    html.Br()
])

@app.callback(
    Output('graph-3', 'figure'),
    [Input('b11', 'value'),
     Input('b12', 'value'),
     Input('w11', 'value'),
     Input('w12', 'value'),
     Input('w21', 'value'),
     Input('w22', 'value'),
     Input('b21', 'value')]
)
def updater(a, b, c, d, e, f, g):
    l1 = log_sigmoid(c * p + a)
    l11 = log_sigmoid(d * p + b)
    func = lambda p, a, b, c, d, e, f, g: purelin(l1 * e + l11 * f + g)
    value = func(p, a, b, c, d, e, f, g)
    fig = px.line(x=p, y=value)
    return fig

# RBF layout
p2 = np.linspace(-3, 3, 1000)
rbf_layout= html.Div([
    # Image and Graph row
    html.Div([
        html.Div([
            html.Br(),html.Br(),html.Br(),
            html.Img(src="https://github.com/Osemekhian/ghost/blob/main/rbf.png?raw=true")
        ], style={'width': '48%', 'display': 'inline-block'}),

        html.Div([
            dcc.Graph(id='graph-4')
        ], style={'width': '48%', 'display': 'inline-block', 'float': 'right'})
    ]),

    html.Br(), html.Br(),html.Br(), html.Br(),html.Br(),html.Br(),

    dbc.Row([
        dbc.Col([  # Left column for sliders (4 sliders)
            html.P('b1'),
            dcc.Slider(id='b1',
                       min=-5,
                       max=5,
                       value=1,
                       step=0.1,
                       marks={i: f"{i}" for i in range(-10, 10, 1)},
                       tooltip={"placement": "bottom", "always_visible": False}
                       ),

            html.P('w1'),
            dcc.Slider(id='w1',
                       min=-5,
                       max=5,
                       value=0,
                       step=0.1,
                       marks={i: f"{i}" for i in range(-10, 10, 1)},
                       tooltip={"placement": "bottom", "always_visible": False}
                       )
        ], width=6),

        dbc.Col([  # Right column for sliders (3 sliders)
            html.P('w2'),
            dcc.Slider(id='w2',
                       min=-5,
                       max=5,
                       value=1,
                       step=0.1,
                       marks={i: f"{i}" for i in range(-10, 10, 1)},
                       tooltip={"placement": "bottom", "always_visible": False}
                       ),
            html.P('b2'),
            dcc.Slider(id='b2',
                       min=-5,
                       max=5,
                       value=0,
                       step=0.1,
                       marks={i: f"{i}" for i in range(-10, 10, 1)},
                       tooltip={"placement": "bottom", "always_visible": False}
                       ),
        ], width=6)
    ]),

    html.Br()
])

@app.callback(Output('graph-4','figure'),
              [Input('b1','value'),
               Input('w1','value'),
               Input('w2','value'),
               Input('b2','value')])
def updater(b1,w1,w2,b2):
    n= p2.shape[0]
    a1= (w1-p2)**2
    a1= gaussian((np.sqrt(a1))*b1)
    a2= purelin(w2*a1 + b2)
    fig = px.line(x=p2, y=a2)
    return fig

#================================
@app.callback(
    Output('tabout','children'),
          Input('tab1','value')
)
def update(tab):
    if tab== 'MLP':
        return mlp_layout
    if tab== 'RBF':
        return rbf_layout

if __name__ == "__main__":
    app.run_server(
        debug=True,
        port=8080,
        host="0.0.0.0"
    )

    # app.run_server(
    #     debug=True,
    #     port=8080,
    #     host="0.0.0.0",
    # )
