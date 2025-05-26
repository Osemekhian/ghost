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
from scipy.spatial.distance import cdist
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
# p2 = np.linspace(-2, 2, 1000).reshape(-1,1)
rbf_layout= html.Div([
    # Image and Graph row
    html.Div([
        html.Div([
            html.Br(),html.Br(),html.Br(),
            html.Img(src=b64_image("rbf.png"))
        ], style={'width': '48%', 'display': 'inline-block'}),

        html.Div([
            dcc.Graph(id='graph-4')
        ], style={'width': '48%', 'display': 'inline-block', 'float': 'right'})
    ]),

    html.Br(), html.Br(),html.Br(), html.Br(),html.Br(),html.Br(),

    dbc.Row([
        dbc.Col([  # Left column for sliders (4 sliders)
            html.P('b11'),
            dcc.Slider(id='b11_',
                       min=-2,
                       max=2,
                       value=2,
                       step=0.1,
                       marks={i: f"{i}" for i in range(-10, 10, 1)},
                       tooltip={"placement": "bottom", "always_visible": False}
                       ),
            html.P('b12'),
            dcc.Slider(id='b12_',
                       min=-2,
                       max=2,
                       value=2,
                       step=0.1,
                       marks={i: f"{i}" for i in range(-10, 10, 1)},
                       tooltip={"placement": "bottom", "always_visible": False}
                       ),

            html.P('w11'),
            dcc.Slider(id='w11_',
                       min=-2,
                       max=2,
                       value=-1,
                       step=0.1,
                       marks={i: f"{i}" for i in range(-10, 10, 1)},
                       tooltip={"placement": "bottom", "always_visible": False}
                       ),
            html.P('w12'),
            dcc.Slider(id='w12_',
                       min=-2,
                       max=2,
                       value=1,
                       step=0.1,
                       marks={i: f"{i}" for i in range(-10, 10, 1)},
                       tooltip={"placement": "bottom", "always_visible": False}
                       )
        ], width=6),

        dbc.Col([  # Right column for sliders (3 sliders)
            html.P('w21'),
            dcc.Slider(id='w21_',
                       min=-2,
                       max=2,
                       value=1,
                       step=0.1,
                       marks={i: f"{i}" for i in range(-10, 10, 1)},
                       tooltip={"placement": "bottom", "always_visible": False}
                       ),
            html.P('w22'),
            dcc.Slider(id='w22_',
                       min=-2,
                       max=2,
                       value=1,
                       step=0.1,
                       marks={i: f"{i}" for i in range(-10, 10, 1)},
                       tooltip={"placement": "bottom", "always_visible": False}
                       ),
            html.P('b2'),
            dcc.Slider(id='b2',
                       min=-2,
                       max=2,
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
              [Input('b11_','value'),
               Input('b12_','value'),
               Input('b2','value'),
               Input('w11_','value'),
               Input('w12_', 'value'),
               Input('w21_', 'value'),
               Input('w22_', 'value')
               ])
def updater(b11,b12,b2,w11,w12,w21,w22):
    p = np.linspace(-2, 2, 400).reshape(-1,1)
    W1 = np.array([[w11], [w12]])
    b1 = np.array([b11, b12])
    W2 = np.array([[w21, w22]])
    b2 = np.array([b2])
    p = np.atleast_2d(p)
    if p.shape[1] != W1.shape[1]:  # If p is (n_samples,) reshape to (n_samples, R)
        p = p.reshape(-1, W1.shape[1])
    dist = cdist(p, W1, metric='euclidean')
    dist= dist.T
    n1 = dist * b1[:, np.newaxis]
    a1 = gaussian(n1)
    n2 = np.dot(W2, a1) + b2
    a2 = n2.ravel()
    fig = px.line(x=p.ravel(),y=a2)
    #fig.update_yaxes(range=[-2, 2])
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
