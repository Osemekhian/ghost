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
import matplotlib.pyplot as plt
import plotly.express as px
from datetime import date
from skimage import io
from skimage.io import imsave
import io as IO
import base64
import random
style={'textAlign':'center'}
steps=0.1
marks= lambda min,max:{i:f"{i}" for i in range(min,max)}
#===========================================
def datum():
    dat = pd.read_csv(
        'https://docs.google.com/spreadsheets/d/e/2PACX-1vTiQBygf4Uo45gGW4qfdO5ekeyYSz6O9JP9SkBogtLSzlGrE5bMa0pJy2voQakRf_izgZwzU3WwVaA_/pub?gid=593030798&single=true&output=csv')
    return dat

my_app= dash.Dash(__name__,external_stylesheets=[dbc.themes.SOLAR]) #dbc.themes.MORPH

my_app.layout = html.Div([
    html.H1('Denny"s DashBoard'),html.Br(),
    html.P('Store:'),
    dcc.Dropdown(id='drop1',
                 options=[{'label': i, 'value': i} for i in ['Benning Road','Bladensburg']],
                 multi=False,
                 value=["Benning Road"],placeholder='Select Store...'), html.Br(),
    html.P('Date:'),
    dcc.DatePickerSingle(
        id='my-date-picker-single',
        min_date_allowed=date(2023, 1, 1),
        max_date_allowed=date(2030, 1, 1),
        initial_visible_month=date(2023, 1, 4),
        date=date(2023, 1, 4)),
    html.Div(id='out')
],style=style)

@my_app.callback(
    Output('out', 'children'),
    [Input('my-date-picker-single', 'date'),
     Input('drop1', 'value')])
def update(a,b):
    df = pd.read_csv(
        'https://docs.google.com/spreadsheets/d/e/2PACX-1vTiQBygf4Uo45gGW4qfdO5ekeyYSz6O9JP9SkBogtLSzlGrE5bMa0pJy2voQakRf_izgZwzU3WwVaA_/pub?gid=593030798&single=true&output=csv')
    date_object = date.fromisoformat(a)
    date_string = date_object.strftime('%m/%d/%Y')
    filter = df[df.Date == date_string]
    filter = df[df.Store == b]
    imgs=[]
    for i in range(len(filter)):
        filter['Image (Dashboard)'].iloc[i] = filter['Image (Dashboard)'].iloc[i].replace('open?', 'uc?')+'&export=download'
    for i in range(len(filter)):
        imgs.append([io.imread(filter.iloc[:,-1].iloc[i])])
    idx=1
    plt.figure(figsize=(20,20))
    for i in range(len(filter)):
        plt.subplot(2, 2, idx)
        plt.imshow(imgs[i][0])
        plt.axis('off')
        idx +=1
    buf = IO.BytesIO()  # in-memory files
    plt.savefig(buf, format="png")  # save to the above file object
    plt.close()
    data = base64.b64encode(buf.getbuffer()).decode("utf8")  # encode to html elements
    final = "data:image/png;base64,{}".format(data)

    return html.Img(src=final)

if __name__ == '__main__':
    my_app.run_server(
        port=random.randint(8000, 9999),  # 8080
        host="127.0.0.1"
    )


