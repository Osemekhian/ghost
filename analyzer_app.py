import dash as dash
from dash import dcc,dash_table,State
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
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.preprocessing import LabelEncoder
#from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.linear_model import LinearRegression, LogisticRegression, Ridge, Lasso, ElasticNet
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, GradientBoostingRegressor, GradientBoostingClassifier,AdaBoostClassifier,AdaBoostRegressor
from sklearn.svm import SVC, SVR
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.metrics import accuracy_score, mean_squared_error, confusion_matrix, mean_absolute_error, classification_report, r2_score
from scipy.stats import uniform, randint, uniform, loguniform
import plotly.io as pio
pio.templates.default = "gridon" #"plotly"
style={'textAlign':'center'}
style2={'width': '80%',
        'borderWidth': '1px',
        'borderStyle': 'dashed',
        'borderRadius': '5px',
        'textAlign': 'center',
        'background-color':'#485785',
        'color':'white',
        'align-items':'center',
        'margin':'auto'
    }
box_style = {
        'border': '1px solid #ccc',
        'borderRadius': '8px',
        'padding': '10px',
        'marginBottom': '10px',
        #'boxShadow': '0 2px 8px rgba(0,0,0,0.1)',
        'background': 'linear-gradient(to bottom,#e5e5e5, #c0c0c0, #a0a0a0)'  # Light purple background
    }
steps=0.1
random_state= 42
marks= lambda min,max:{i:f"{i}" for i in range(min,max)}
models= ['LinearRegression','LogisticRegression','RandomForestRegressor','RandomForestClassifier','SVM Regression',
         'SVM Classification', 'Naive Bayes Classifier','KNeighborsClassifier','KNeighborsRegressor',
         'Ridge Regression','Lasso Regression','ElasticNet Regression']
# 'AdaBoostClassifier','AdaBoostRegressor','GradientBoostingRegressor','GradientBoostingClassifier'
#===========================================
# Data cleaner functions
def remove_outliers(df,column):
    if df[column].dtype == 'int' or df[column].dtype == 'float':
        q1= df[column].quantile(0.25)
        q3= df[column].quantile(0.75)
        iqr= q3-q1
        lb= q1-1.5*iqr
        ub= q3-1.5*iqr
        df_new= df[(df[column]>= lb) & (df[column]<=ub)]
    return df_new

def id_checker(df, dtype='float'):
    """
    The identifier checker

    Parameters
    ----------
    df : dataframe
    dtype : the data type identifiers cannot have, 'float' by default
            i.e., if a feature has this data type, it cannot be an identifier

    Returns
    ----------
    The dataframe of identifiers
    """

    # Get the dataframe of identifiers
    df_id = df[[var for var in df.columns
                # If the data type is not dtype
                if (df[var].dtype != dtype
                    # If the value is unique for each sample
                    and df[var].nunique(dropna=True) == df[var].notnull().sum())]]
    # df_train.drop(columns=np.intersect1d(df_id.columns, df_train.columns), inplace=True)

    return df_id


def cleaner(df):
    df= df.drop_duplicates()
    df.columns= (df.columns.str.strip().str.lower().str.replace(" ","_").str.replace(
        "[()$@!#%^&*-=+~`/\|]","", regex=True
    ))

    df= df.dropna(axis='columns', how='all')
    df= df.dropna(how='all') #by rows on default

    for col in df.columns:
        if 'date' in col or 'time' in col:
            try:
                df[col]= pd.to_datetime(df[col])
            except:
                pass

        if df[col].isna().sum().all():
            if df[col].dtype == 'object':
                df[col].fillna(df[col].mode().max(), inplace=True)
            elif df[col].dtype == 'int':
                df[col].fillna(round(df[col].mean()), inplace=True)
            elif df[col].dtype == 'float':
                df[col].fillna(np.round(df[col].mean(),2), inplace=True)
            else:
                pass
        else:
            pass

    return df

def preprocess(df, target, features):
    if target in features:
        df= df[features]
    else:
        features += [target]
        df = df[features]

    df = cleaner(df)
    identifiers = id_checker(df).columns
    df = df.drop(columns=identifiers)
    tag_type= df[target].dtype
    if df[target].dtype == 'object':
        tsf= LabelEncoder().fit(df[target])
        target_column= tsf.transform(df[target])
    else:
        target_column= df[target]
        tsf= None

    df= df.drop(columns=target)

    numerical_columns= df.select_dtypes(include=['float64','int64']).columns
    categorical_columns= df.select_dtypes(include=['object']).columns

    for i in categorical_columns:
        df[i]= LabelEncoder().fit_transform(df[i])

    model_cols= numerical_columns.append(categorical_columns)
    X = df[model_cols]
    Y = target_column
    if tag_type == 'object':
        x_train, x_test, y_train, y_test = train_test_split(X, Y, test_size=0.15,stratify=Y, random_state=random_state)
    else:
        x_train, x_test, y_train, y_test = train_test_split(X, Y, test_size=0.15, random_state=random_state)
    sc = StandardScaler().fit(x_train)
    x_train = sc.transform(x_train)
    x_test = sc.transform(x_test)

    return tsf, sc, x_train, x_test, y_train, y_test

def convert_string_to_appropriate_type(s):
    try:
        return int(s)
    except ValueError:
        try:
            return float(s)
        except ValueError:
            return s

def convert_list(lst):
    return [convert_string_to_appropriate_type(item) for item in lst]

def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
            return df
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
            return df
    except:
        return ""
             
#===========================================

my_app= dash.Dash(__name__,external_stylesheets=[dbc.themes.LUX],suppress_callback_exceptions=True) #dbc.themes.MORPH | dbc.themes.SOLAR
server= my_app.server

# my_app.title= "Data Analyzer"
my_app.index_string='''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>Data Analyzer</title>
        <link rel="icon" href="https://raw.githubusercontent.com/Osemekhian/ghost/refs/heads/main/file-HFcKPxRscWybi9pdrJfJ8e.webp" type="image/x-icon">
        {%css%}
        <style>
            .hover-tile {
                transition: all 0.3s ease;
                border: 2px solid #999;
                border-radius: 12px;
                padding: 15px;
                background: linear-gradient(to bottom, #e5e5e5, #c0c0c0, #a0a0a0);  /* light to silver */
                color: #000;  /* Black text for contrast */
                margin-bottom: 10px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }

            .hover-tile:hover {
                border-color: #666;
                box-shadow: 0 6px 15px rgba(0, 0, 0, 0.3);
                transform: scale(1.02);
                background: linear-gradient(to bottom, #d8d8d8, #b0b0b0, #888888); /* darker on hover */
                cursor: pointer;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''
my_app.layout= dbc.Container([ html.Div([
    html.P(""),
    html.H1("Data Analyzer"),
    html.P("by: Osemekhian Solomon Ehilen"),html.Br(),
    dcc.Markdown("""This Web App Collects Your ***Data(Link or Upload)*** 
                    then Generates Your Analysis & Model"""),
    #=================
    dbc.Input(id="in1",placeholder="Paste Link to Your Data...",type='text', size="lg", className="mb-3"),
    html.Pre('For example: https://raw.githubusercontent.com/datasciencedojo/datasets/refs/heads/master/titanic.csv'),
    html.Div([dcc.Upload(id='upload-data',children=html.Div(['Drag and Drop or ',html.A('Select Data File')]),style={
        'width': '50%',
        'height': '60px',
        'lineHeight': '60px',
        'borderWidth': '1px',
        'borderStyle': 'dashed',
        'borderRadius': '5px',
        'textAlign': 'center',
        'background-color':'#000000',
        'color':'white',
        'align-items':'center',
        'margin':'auto'
    })]),
    #==================
    html.Br(),
    dcc.RadioItems(options=['Raw Data', 'Cleaned Data'], value='Raw Data', id='radio'),
    html.Button("Download Cleaned Data",id='btn_csv',n_clicks=0),html.Br(),
    dcc.Download(id='download-data-cleaned'), html.Pre("One-time Download Per Session"),html.Br(),
    html.P('Remove outliers using one numerical column:'),
    dcc.Dropdown(id='drp', multi=False),
    dcc.Checklist(options=['Remove Outliers'], id='outlier'),
    dcc.Loading(id='loading11',children=html.Div(id="out1", className="mt-3 text-center")),
    html.Br(),html.Div(id='outy'),
    html.Div(id='out2'),
    dcc.Store(id='store1'),html.Br(),

    html.H4("Univariate Charts"), html.Br(),
    html.P("Select Column:"),
    dcc.Dropdown(id='unidrp',multi=False),
    dcc.Loading(id='loading', children=html.Div(id='uni',className="mt-3 text-center")), html.Br(),

    html.H4("Bivariate Charts"), html.Br(),
    html.P('NB:Tweak the column selections to get some charts as desired'),
    html.P("Select Columns (2 max):"),
    dcc.Dropdown(id='bidrp',multi=True),
    dcc.Loading(id='loading2', children=html.Div(id='Bi',className="mt-3 text-center")),

    html.Div(id='out3'), html.Br(),


    html.H4("Modeling"),
    html.P("Please select feature columns excluding target which is selected above:"),
    dcc.Dropdown(id='mod2drp',multi=True,placeholder="select features only..."),
    html.P("Please select target variable/column:"),
    dcc.Dropdown(id='moddrp',multi=False, placeholder="select target only..."),
    html.P("Please select model:"),
    dcc.Dropdown(id='modeldrp',options= [{'label':i,'value':i} for i in models]),
    html.Button("Analyze",id='btn_analyze'), html.Br(),html.Br(),

    dcc.Loading(id='loading3', children=html.Div(id='modelout',className="mt-3 text-center")),
    dcc.Store(id='store2'),dcc.Store(id='store3lt'),dcc.Store(id='store4sc'),
    html.Br(),

    html.H4("Prediction Arena"),
    html.Pre('Insert the appropriate features for prediction'),
    dbc.Input(id='in2',placeholder='type in the features seperated by comma...', type='text'),
    html.Br(),
    dcc.Loading(id='loading4', children=html.Div(id='predout',className="mt-3 text-center")), html.Br(),


    dcc.Markdown("Bravelion | 2025 | Contact for Analysis: [email](mailto:oseme781227@gmail.com) ")
], style=style)

],fluid=True)

@my_app.callback([Output('out1','children'),
                        Output('outy','children'),
                        Output('out2','children'),
                        Output('store1', 'data'),
                        Output('unidrp','options'),
                        Output('bidrp','options'),
                        Output('drp','options'),
                        Output('moddrp','options'),
                        Output('mod2drp','options')],
                       [Input('in1','value'),
                        Input('upload-data','contents'),
                        State('upload-data','filename'),
                        Input('radio','value'),
                        Input('outlier','value'),
                        Input('drp','value')]
                )
def link(text,contents, filename, rad, button, drpval):
    # if text==None:
    #     return ""
    if contents is not None:
        try:
            if button:
                data = parse_contents(contents, filename)
                data.columns = (data.columns.str.strip().str.lower().str.replace(" ", "_").str.replace(
                    "[()$@!#%^&*-=+~`/\|]", "", regex=True))

                if rad == 'Cleaned Data':
                    data = cleaner(data)
                    if data[drpval].dtype == 'object':
                        pass
                    else:
                        data = remove_outliers(data, drpval)
                else:
                    data = remove_outliers(data, drpval)
            else:
                data = parse_contents(contents, filename)
                data.columns = (data.columns.str.strip().str.lower().str.replace(" ", "_").str.replace(
                    "[()$@!#%^&*-=+~`/\|]", "", regex=True))

            if rad == 'Raw Data':
                df = data
                options = [{'label': col, 'value': col} for col in df.columns]
                desc = df.describe()
                desc.insert(0, 'stat', df.describe().index)
                return (html.Div(dash_table.DataTable(df.to_dict('records'),
                                                      [{"name": i, "id": i} for i in df.columns],
                                                      style_table={'overflowX': 'auto'},
                                                      style_cell={'textAlign': 'left', 'padding': '5px'},
                                                      style_header={'backgroundColor': 'rgb(220, 220, 220)',
                                                                    'fontWeight': 'bold'},
                                                      page_size=10,
                                                      style_data={"overflow": "hidden", "textOverflow": "ellipsis",
                                                                  "maxWidth": 0}),className="hover-tile"), html.H3("Data Description"),
                        html.Div(dash_table.DataTable(desc.to_dict('records'),
                                                      [{"name": i, "id": i} for i in desc.columns],
                                                      style_table={'overflowX': 'auto'},
                                                      style_cell={'textAlign': 'left', 'padding': '5px'},
                                                      style_header={'backgroundColor': 'rgb(220, 220, 220)',
                                                                    'fontWeight': 'bold'},
                                                      page_size=20,
                                                      style_data={"overflow": "hidden", "textOverflow": "ellipsis",
                                                                  "maxWidth": 0}),className="hover-tile"),
                        df.to_json(orient='table'), options, options, options, options, options)
            else:
                df = cleaner(data)
                options = [{'label': col, 'value': col} for col in df.columns]
                desc = df.describe()
                desc.insert(0, 'stat', df.describe().index)
                return (html.Div(dash_table.DataTable(df.to_dict('records'),
                                                      [{"name": i, "id": i} for i in df.columns],
                                                      style_table={'overflowX': 'auto'},
                                                      style_cell={'textAlign': 'left', 'padding': '5px'},
                                                      style_header={'backgroundColor': 'rgb(220, 220, 220)',
                                                                    'fontWeight': 'bold'},
                                                      page_size=10,
                                                      style_data={"overflow": "hidden", "textOverflow": "ellipsis",
                                                                  "maxWidth": 0}),className="hover-tile"), html.H3("Data Description"),
                        html.Div(dash_table.DataTable(desc.to_dict('records'),
                                                      [{"name": i, "id": i} for i in desc.columns],
                                                      style_table={'overflowX': 'auto'},
                                                      style_cell={'textAlign': 'left', 'padding': '5px'},
                                                      style_header={'backgroundColor': 'rgb(220, 220, 220)',
                                                                    'fontWeight': 'bold'},
                                                      page_size=20,
                                                      style_data={"overflow": "hidden", "textOverflow": "ellipsis",
                                                                  "maxWidth": 0}),className="hover-tile"),
                        df.to_json(orient='table'), options, options, options, options, options)
        except:
            return '','','','','','','','',''
    else:
    #======
        try:
            if button:
                data= pd.read_csv(text,low_memory=False)
                data.columns = (data.columns.str.strip().str.lower().str.replace(" ", "_").str.replace(
                    "[()$@!#%^&*-=+~`/\|]", "", regex=True))

                if rad== 'Cleaned Data':
                    data= cleaner(data)
                    if data[drpval].dtype == 'object':
                        pass
                    else:
                        data= remove_outliers(data, drpval)
                else:
                    data = remove_outliers(data, drpval)
            else:
                data = pd.read_csv(text, low_memory=False)
                data.columns = (data.columns.str.strip().str.lower().str.replace(" ", "_").str.replace(
                    "[()$@!#%^&*-=+~`/\|]", "", regex=True))

            if rad == 'Raw Data':
                df= data
                options = [{'label': col, 'value': col} for col in df.columns]
                desc = df.describe()
                desc.insert(0, 'stat', df.describe().index)
                return (html.Div(dash_table.DataTable(df.to_dict('records'),
                                                      [{"name": i, "id": i} for i in df.columns],
                                                      style_table={'overflowX': 'auto'},
                                                      style_cell={'textAlign': 'left', 'padding': '5px'},
                                                      style_header={'backgroundColor': 'rgb(220, 220, 220)',
                                                                    'fontWeight': 'bold'},
                                                      page_size=10,
                                                      style_data={"overflow": "hidden", "textOverflow": "ellipsis",
                                                                  "maxWidth": 0}),className="hover-tile"), html.H3("Data Description"),
                        html.Div(dash_table.DataTable(desc.to_dict('records'),
                                                      [{"name": i, "id": i} for i in desc.columns],
                                                      style_table={'overflowX': 'auto'},
                                                      style_cell={'textAlign': 'left', 'padding': '5px'},
                                                      style_header={'backgroundColor': 'rgb(220, 220, 220)',
                                                                    'fontWeight': 'bold'},
                                                      page_size=20,
                                                      style_data={"overflow": "hidden", "textOverflow": "ellipsis",
                                                                  "maxWidth": 0}),className="hover-tile"),
                        df.to_json(orient='table'), options, options, options,options,options)
            else:
                df= cleaner(data)
                options = [{'label': col, 'value': col} for col in df.columns]
                desc = df.describe()
                desc.insert(0, 'stat', df.describe().index)
                return (html.Div(dash_table.DataTable(df.to_dict('records'),
                                              [{"name": i, "id": i} for i in df.columns],
                                              style_table={'overflowX': 'auto'},
                                              style_cell={'textAlign': 'left','padding':'5px'},
                                              style_header={'backgroundColor':  'rgb(220, 220, 220)','fontWeight': 'bold'},
                                                     page_size=10, style_data={"overflow":"hidden","textOverflow":"ellipsis",
                                                                               "maxWidth":0}),className="hover-tile"),html.H3("Data Description"),html.Div(dash_table.DataTable(desc.to_dict('records'),
                                              [{"name": i, "id": i} for i in desc.columns],
                                              style_table={'overflowX': 'auto'},
                                              style_cell={'textAlign': 'left','padding':'5px'},
                                              style_header={'backgroundColor':  'rgb(220, 220, 220)','fontWeight': 'bold'},
                                                     page_size=20, style_data={"overflow":"hidden","textOverflow":"ellipsis",
                                                                               "maxWidth":0}),className="hover-tile"),
                        df.to_json(orient='table'), options,options, options, options,options)
        except:
            return '','','','','','','','',''

@my_app.callback(Output('uni','children'),
                 [Input('store1','data'),
                  Input('unidrp','value'),
                  Input('radio','value'),
                  Input('outlier','value')])
def chart(data, column, rad, button):
    try:
        if button:
            pass
        if rad:
            df = pd.read_json(data, orient='table')
            fig = px.histogram(df, x=column, title=f"Histogram Plot for {column}")
            fig2 = px.box(df, y=column, title=f" Box Plot for {column}")
            fig3 = px.line(df, y=column, title=f" Line Plot for {column}")

            return dbc.Container([
                                    dbc.Row([
                                    dbc.Col(html.Div(dcc.Graph(figure=fig), className="hover-tile", style=box_style),xs=12, sm=12, md=6, lg=6),
                                    dbc.Col(html.Div(dcc.Graph(figure=fig2), className="hover-tile", style=box_style), xs=12, sm=12, md=6, lg=6),
                                    ], className="mb-4"),  # margin-bottom for spacing
                                    dbc.Row([
                                    dbc.Col(html.Div(dcc.Graph(figure=fig3), className="hover-tile", style=box_style), width=12)
                                ])
                            ])
    except:
        return ""

@my_app.callback(Output('Bi','children'),
                 [Input('store1','data'),
                  Input('bidrp','value'),
                  Input('radio', 'value'),
                  Input('outlier', 'value')])
def charts(data, columns, rad, button):
    try:
        button = True
        if button:
            # pass
            if rad:
                columns = columns[:2]
                df = pd.read_json(data, orient='table')
                cor = df.corr(numeric_only=True).round(2)
                fig2 = px.box(df, x=columns[0], y=columns[-1],
                              title=f"Box Plot for {columns[0]} & {columns[-1]}")  # points='all',
                fig3 = px.scatter(df, x=columns[0], y=columns[-1],
                                  title=f"Scatter Plot for {columns[0]} & {columns[-1]}")
                fig4 = px.imshow(cor, text_auto=True, title=f"Heatmap Correlation Plot", aspect="auto")
                fig4.update_xaxes(side="bottom")
                fig5 = px.pie(df, values=columns[0], names=columns[-1], hole=0.1,
                              title=f"Pie Plot for {columns[0]} & {columns[-1]}")
                fig = px.bar(df, x=columns[0], y=columns[-1], title=f"Bar Plot for {columns[0]} & {columns[-1]}")

                return dbc.Container([
                                    dbc.Row([
                                    dbc.Col(html.Div(dcc.Graph(figure=fig2), className="hover-tile", style=box_style),xs=12, sm=12, md=6, lg=6),
                                    dbc.Col(html.Div(dcc.Graph(figure=fig3), className="hover-tile", style=box_style), xs=12, sm=12, md=6, lg=6),
                                    ], className="mb-2"),

				    dbc.Row([
                                    dbc.Col(html.Div(dcc.Graph(figure=fig4), className="hover-tile", style=box_style),xs=12, sm=12, md=6, lg=6),
                                    dbc.Col(html.Div(dcc.Graph(figure=fig), className="hover-tile", style=box_style), xs=12, sm=12, md=6, lg=6),
                                    ], className="mb-2"),

				    dbc.Row([
                                    dbc.Col(html.Div(dcc.Graph(figure=fig5), className="hover-tile", style=box_style), width=12)
                                ])
                            ])
    except:
        return ""
#======================================================================================
@my_app.callback(Output('modelout','children'),
                       Output('store2', 'data'),
                       Output('store3lt', 'data'),
                       Output('store4sc', 'data'),
                     [Input('store1','data'),
                      Input('modeldrp','value'),
                      Input('moddrp', 'value'),
                      Input('mod2drp','value'),
                      Input('btn_analyze', 'n_clicks')])
def out1( data, model_type, target, features, btn_analyze):
    try:
        if btn_analyze:
            df= pd.read_json(data, orient='table')
            label_transform, standard_scaler, x_train, x_test, y_train, y_test = preprocess(df,target,features)

            if df[target].dtype == 'object':
                if model_type == 'LogisticRegression':
                    model= LogisticRegression(random_state=random_state)
                    param_dist = {
                        'C': uniform(0.001, 1000),  # Uniform distribution for C
                        'penalty': ['l1', 'l2'],  # Regularization type
                        'solver': ['liblinear', 'saga'],  # Solvers that support L1 and L2
                        'max_iter': randint(50, 500),  # Random integer between 50 and 500
                        'class_weight': [None, 'balanced'],  # Handle class imbalance
                        'fit_intercept': [True, False],  # Whether to fit intercept
                        'tol': uniform(1e-4, 1e-2),  # Tolerance for stopping criteria
                    }
                    # Initialize RandomizedSearchCV
                    random_search = RandomizedSearchCV(
                        estimator=model,
                        param_distributions=param_dist,
                        n_iter=10,  # Number of parameter settings to sample
                        scoring='accuracy',  # Metric to evaluate
                        cv=5,  # Number of cross-validation folds
                        random_state=42,
                        n_jobs=1,  # Use all available CPU cores
                    )
                elif model_type =='RandomForestClassifier':
                    model= RandomForestClassifier(random_state=random_state)
                    param_dist = {
                        'n_estimators': randint(50, 100),  # Number of trees
                        'max_depth': [None] + list(randint(10, 50).rvs(5)),  # Maximum depth
                        'min_samples_split': randint(2, 20),  # Minimum samples to split
                        'min_samples_leaf': randint(1, 10),  # Minimum samples at leaf
                        'max_features': ['auto', 'sqrt', 'log2', 0.5],  # Features to consider
                        'bootstrap': [True, False],  # Bootstrap sampling
                        'criterion': ['gini', 'entropy'],  # Split criterion
                        'max_leaf_nodes': [None] + list(randint(10, 50).rvs(5)),  # Maximum leaf nodes
                        'min_impurity_decrease': uniform(0.0, 0.2),  # Impurity decrease
                        'class_weight': [None, 'balanced'],  # Class weights
                    }
                    # Initialize RandomizedSearchCV
                    random_search = RandomizedSearchCV(
                        estimator=model,
                        param_distributions=param_dist,
                        n_iter=3,  # Number of parameter settings to sample
                        scoring='accuracy',  # Metric to evaluate
                        cv=5,  # Number of cross-validation folds
                        random_state=42,
                        n_jobs=1,  # Use all available CPU cores
                    )
                elif model_type == 'AdaBoostClassifier':
                    model = AdaBoostClassifier(random_state=42)
                    param_dist = {
                        'n_estimators': randint(50, 100),  # Number of weak learners
                        'learning_rate': uniform(0.001, 1.0),  # Learning rate
                        'base_estimator': [DecisionTreeClassifier(max_depth=1), DecisionTreeClassifier(max_depth=2)],
                        'algorithm': ['SAMME', 'SAMME.R'],  # Algorithm to use
                    }
                    # Initialize RandomizedSearchCV
                    random_search = RandomizedSearchCV(
                        estimator=model,
                        param_distributions=param_dist,
                        n_iter=3,  # Number of parameter settings to sample
                        scoring='accuracy',  # Metric to evaluate
                        cv=5,  # Number of cross-validation folds
                        random_state=42,
                        n_jobs=1,
                    )
                elif model_type == 'GradientBoostingClassifier':
                    model= GradientBoostingClassifier(random_state=random_state)
                    param_dist = {
                        'n_estimators': randint(50, 100),  # Number of boosting stages
                        'learning_rate': uniform(0.001, 0.2),  # Learning rate
                        'max_depth': randint(3, 15),  # Maximum depth of trees
                        'min_samples_split': randint(2, 20),  # Minimum samples to split
                        'min_samples_leaf': randint(1, 10),  # Minimum samples at leaf
                        'max_features': ['auto', 'sqrt', 'log2', 0.5],  # Features to consider
                        'subsample': uniform(0.5, 0.5),  # Fraction of samples for fitting
                        'loss': ['deviance', 'exponential'],  # Loss function
                        'criterion': ['friedman_mse', 'mse'],  # Split criterion
                        'min_impurity_decrease': uniform(0.0, 0.2),  # Impurity decrease
                        'warm_start': [True, False],  # Warm start
                    }
                    # Initialize RandomizedSearchCV
                    random_search = RandomizedSearchCV(
                        estimator=model,
                        param_distributions=param_dist,
                        n_iter=2,  # Number of parameter settings to sample
                        scoring='accuracy',  # Metric to evaluate
                        cv=5,  # Number of cross-validation folds
                        random_state=42,
                        n_jobs=1,  # Use all available CPU cores
                    )
                elif model_type == 'SVM Classification':
                    model= SVC(random_state=random_state)
                    param_dist = {
                        'C': loguniform(1e-2, 1e2),  # Regularization parameter (log-uniform distribution)
                        'kernel': ['linear', 'rbf', 'poly'],  # Kernel type
                        'gamma': ['scale', 'auto'] + list(loguniform(1e-3, 1e1).rvs(5)),  # Kernel coefficient
                        'degree': randint(2, 5),  # Degree for polynomial kernel
                        'coef0': uniform(0.0, 1.0),  # Independent term in kernel
                        'shrinking': [True, False],  # Shrinking heuristic
                        'probability': [True, False],  # Probability estimates
                        'tol': loguniform(1e-4, 1e-2),  # Tolerance for stopping criteria
                        'class_weight': [None, 'balanced'],  # Class weights
                    }
                    # Initialize RandomizedSearchCV
                    random_search = RandomizedSearchCV(
                        estimator=model,
                        param_distributions=param_dist,
                        n_iter=3,  # Number of parameter settings to sample
                        scoring='accuracy',  # Metric to evaluate
                        cv=5,  # Number of cross-validation folds
                        random_state=42,
                        n_jobs=1,  # Use all available CPU cores
                    )
                elif model_type =='Naive Bayes Classifier':
                    model= GaussianNB()
                    param_dist = {
                        'var_smoothing': loguniform(1e-9, 1e-5),  # Smoothing parameter
                    }
                    # Initialize RandomizedSearchCV
                    random_search = RandomizedSearchCV(
                        estimator=model,
                        param_distributions=param_dist,
                        n_iter=5,  # Number of parameter settings to sample
                        scoring='accuracy',  # Metric to evaluate
                        cv=5,  # Number of cross-validation folds
                        random_state=42,
                        n_jobs=1,  # Use all available CPU cores
                    )
                elif model_type == 'KNeighborsClassifier':
                    model= KNeighborsClassifier()
                    param_dist = {
                        'n_neighbors': randint(3, 20),  # Number of neighbors
                        'weights': ['uniform', 'distance'],  # Weight function
                        'p': [1, 2],  # Power parameter for Minkowski metric
                        'metric': ['minkowski', 'euclidean', 'manhattan','chebyshev'],  # Algorithm for nearest neighbors
                    }
                    # Initialize RandomizedSearchCV
                    random_search = RandomizedSearchCV(
                        estimator=model,
                        param_distributions=param_dist,
                        n_iter=5,  # Number of parameter settings to sample
                        scoring='accuracy',  # Metric to evaluate (negative MSE for regression)
                        cv=5,  # Number of cross-validation folds
                        random_state=42,
                        n_jobs=1,  # Use all available CPU cores
                    )
            else:
                if model_type == 'LinearRegression':
                    random_search= LinearRegression() #renamed from model for generality
                elif model_type == 'RandomForestRegressor':
                    model= RandomForestRegressor(random_state=random_state)
                    param_dist = {
                        'n_estimators': randint(50, 100),  # Number of trees
                        'max_depth': [None] + list(randint(10, 50).rvs(5)),  # Maximum depth
                        'min_samples_split': randint(2, 20),  # Minimum samples to split
                        'min_samples_leaf': randint(1, 10),  # Minimum samples at leaf
                        'max_features': ['auto', 'sqrt', 'log2', 0.5],  # Features to consider
                        'bootstrap': [True, False],  # Bootstrap sampling
                    }
                    # Initialize RandomizedSearchCV
                    random_search = RandomizedSearchCV(
                        estimator=model,
                        param_distributions=param_dist,
                        n_iter=3,  # Number of parameter settings to sample
                        scoring='neg_mean_squared_error',  # Metric to evaluate (negative MSE for regression)
                        cv=5,  # Number of cross-validation folds
                        random_state=42,
                        n_jobs=1,  # Use all available CPU cores
                    )
                elif model_type == 'AdaBoostRegressor':
                    model = AdaBoostRegressor(random_state=42)

                    # Define the parameter grid
                    param_dist = {
                        'n_estimators': randint(50, 100),  # Number of weak learners
                        'learning_rate': uniform(0.001, 1.0),  # Learning rate
                        'base_estimator': [DecisionTreeRegressor(max_depth=3), DecisionTreeRegressor(max_depth=5)],
                        'loss': ['linear', 'square', 'exponential'],  # Loss function
                    }
                    # Initialize RandomizedSearchCV
                    random_search = RandomizedSearchCV(
                        estimator=model,
                        param_distributions=param_dist,
                        n_iter=3,  # Number of parameter settings to sample
                        scoring='neg_mean_squared_error',  # Metric to evaluate (negative MSE for regression)
                        cv=5,  # Number of cross-validation folds
                        random_state=42,
                        n_jobs=1,  # Use all available CPU cores
                    )
                elif model_type == 'GradientBoostingRegressor':
                    model= GradientBoostingRegressor(random_state=random_state)
                    param_dist = {
                        'n_estimators': randint(50, 100),  # Number of boosting stages
                        'learning_rate': uniform(0.001, 0.2),  # Learning rate
                        'max_depth': randint(3, 15),  # Maximum depth of trees
                        'min_samples_split': randint(2, 20),  # Minimum samples to split
                        'min_samples_leaf': randint(1, 10),  # Minimum samples at leaf
                        'max_features': ['auto', 'sqrt', 'log2', 0.5],  # Features to consider
                        'subsample': uniform(0.5, 0.5),  # Fraction of samples for fitting
                        'loss': ['ls', 'lad', 'huber'],  # Loss function
                    }
                    # Initialize RandomizedSearchCV
                    random_search = RandomizedSearchCV(
                        estimator=model,
                        param_distributions=param_dist,
                        n_iter=2,  # Number of parameter settings to sample
                        scoring='neg_mean_squared_error',  # Metric to evaluate (negative MSE for regression)
                        cv=5,  # Number of cross-validation folds
                        random_state=42,
                        n_jobs=1,  # Use all available CPU cores
                    )
                elif model_type == 'SVM Regression':
                    model= SVR()
                    param_dist = {
                        'kernel': ['linear', 'rbf', 'poly'],  # Kernel type
                        'C': loguniform(1e-2, 1e2),  # Regularization parameter (log-uniform distribution)
                        'gamma': ['scale', 'auto'] + list(loguniform(1e-3, 1e1).rvs(5)),  # Kernel coefficient
                        'epsilon': uniform(0.01, 1.0),  # Epsilon-tube
                        'degree': randint(2, 5),  # Degree for polynomial kernel
                        'coef0': uniform(0.0, 1.0),  # Independent term in kernel
                        'shrinking': [True, False],  # Shrinking heuristic
                        'tol': loguniform(1e-4, 1e-2),  # Tolerance for stopping criteria
                    }
                    random_search = RandomizedSearchCV(
                        estimator=model,
                        param_distributions=param_dist,
                        n_iter=3,  # Number of parameter settings to sample
                        scoring='neg_mean_squared_error',  # Metric to evaluate (negative MSE for regression)
                        cv=5,  # Number of cross-validation folds
                        random_state=42,
                        n_jobs=1,  # Use all available CPU cores
                    )
                elif model_type == 'KNeighborsRegressor':
                    model= KNeighborsRegressor()
                    param_dist = {
                        'n_neighbors': randint(3, 15),  # Number of neighbors
                        'weights': ['uniform', 'distance'],  # Weight function
                        'p': [1, 2],  # Power parameter for Minkowski metric
                        'algorithm': ['auto', 'ball_tree', 'kd_tree'],  # Algorithm for nearest neighbors
                    }
                    # Initialize RandomizedSearchCV
                    random_search = RandomizedSearchCV(
                        estimator=model,
                        param_distributions=param_dist,
                        n_iter=5,  # Number of parameter settings to sample
                        scoring='neg_mean_squared_error',  # Metric to evaluate (negative MSE for regression)
                        cv=5,  # Number of cross-validation folds
                        random_state=42,
                        n_jobs=1,  # Use all available CPU cores
                    )
                elif model_type == 'Ridge Regression':
                    model= Ridge()
                    param_dist = {
                        'alpha': uniform(0.1, 100),  # Regularization strength
                        'fit_intercept': [True, False],  # Whether to fit intercept
                        'solver': ['auto', 'svd', 'sag'],  # Solver for optimization
                    }
                    # Initialize RandomizedSearchCV
                    random_search = RandomizedSearchCV(
                        estimator=model,
                        param_distributions=param_dist,
                        n_iter=10,  # Number of parameter settings to sample
                        scoring='neg_mean_squared_error',  # Metric to evaluate (negative MSE for regression)
                        cv=5,  # Number of cross-validation folds
                        random_state=42,
                        n_jobs=1,  # Use all available CPU cores
                    )
                elif model_type == 'Lasso Regression':
                    model= Lasso()
                    param_dist = {
                        'alpha': uniform(0.1, 100),  # Regularization strength
                        'fit_intercept': [True, False],  # Whether to fit intercept
                        'selection': ['cyclic', 'random'],  # Coefficient selection method
                    }
                    # Initialize RandomizedSearchCV
                    random_search = RandomizedSearchCV(
                        estimator=model,
                        param_distributions=param_dist,
                        n_iter=10,  # Number of parameter settings to sample
                        scoring='neg_mean_squared_error',  # Metric to evaluate (negative MSE for regression)
                        cv=5,  # Number of cross-validation folds
                        random_state=42,
                        n_jobs=1,  # Use all available CPU cores
                    )
                elif model_type == 'ElasticNet Regression':
                    model= ElasticNet()
                    param_dist = {
                        'alpha': uniform(0.1, 100),  # Regularization strength
                        'l1_ratio': uniform(0.1, 1.0),  # Mixing parameter for L1/L2
                        'fit_intercept': [True, False],  # Whether to fit intercept
                        'selection': ['cyclic', 'random'],  # Coefficient selection method
                    }
                    # Initialize RandomizedSearchCV
                    random_search = RandomizedSearchCV(
                        estimator=model,
                        param_distributions=param_dist,
                        n_iter=10,  # Number of parameter settings to sample
                        scoring='neg_mean_squared_error',  # Metric to evaluate (negative MSE for regression)
                        cv=5,  # Number of cross-validation folds
                        random_state=42,
                        n_jobs=1,  # Use all available CPU cores
                    )


            if df[target].dtype == 'object':
                random_search.fit(x_train, y_train)
                #=====
                buffer = BytesIO()
                joblib.dump(random_search, buffer)  # Write to in-memory buffer
                buffer.seek(0)  # Reset buffer position to read later
                model_bytes = buffer.getvalue()  # Get raw bytes
                model_base64 = base64.b64encode(model_bytes).decode("utf-8")

                buffer2 = BytesIO()
                joblib.dump(label_transform, buffer2)  # Write to in-memory buffer
                buffer2.seek(0)  # Reset buffer position to read later
                lt_bytes = buffer2.getvalue()  # Get raw bytes
                lt_base64 = base64.b64encode(lt_bytes).decode("utf-8")

                buffer3 = BytesIO()
                joblib.dump(standard_scaler, buffer3)  # Write to in-memory buffer
                buffer3.seek(0)  # Reset buffer position to read later
                sc_bytes = buffer3.getvalue()  # Get raw bytes
                sc_base64 = base64.b64encode(sc_bytes).decode("utf-8")
                #=====
                y_pred = random_search.best_estimator_.predict(x_test)
                score = accuracy_score(y_test, y_pred)
                cm = confusion_matrix(y_test, y_pred)
                cm_df= pd.DataFrame(cm,columns=df[target].unique(),index=df[target].unique())
                fig = px.imshow(cm_df, text_auto=True)
                report = classification_report(y_test, y_pred, target_names=df[target].unique())
                return html.Div([html.P(f"The metrics below are based on the test set of your data for {model_type}:"),
                                 html.P(f"Accuracy Score:{score}"), html.Pre(report),
                                 html.P('Confusion Matrix'),html.Pre(cm_df.to_string()),
                                 dcc.Graph(figure=fig), html.Pre(f"Best Parameters for {model_type}\n {random_search.best_params_}")],style=style2,className="hover-tile"),model_base64, lt_base64, sc_base64
            else:
                random_search.fit(x_train, y_train)
                # =====
                buffer = BytesIO()
                joblib.dump(random_search, buffer)  # Write to in-memory buffer
                buffer.seek(0)  # Reset buffer position to read later
                model_bytes = buffer.getvalue()  # Get raw bytes
                model_base64 = base64.b64encode(model_bytes).decode("utf-8")

                buffer2 = BytesIO()
                joblib.dump(label_transform, buffer2)  # Write to in-memory buffer
                buffer2.seek(0)  # Reset buffer position to read later
                lt_bytes = buffer2.getvalue()  # Get raw bytes
                lt_base64 = base64.b64encode(lt_bytes).decode("utf-8")

                buffer3 = BytesIO()
                joblib.dump(standard_scaler, buffer3)  # Write to in-memory buffer
                buffer3.seek(0)  # Reset buffer position to read later
                sc_bytes = buffer3.getvalue()  # Get raw bytes
                sc_base64 = base64.b64encode(sc_bytes).decode("utf-8")
                # =====
                if model_type == 'LinearRegression':
                    y_pred = random_search.predict(x_test)
                    mse = round(mean_squared_error(y_test, y_pred), 4)
                    rmse = np.sqrt(mse)
                    mae = mean_absolute_error(y_test, y_pred)
                    r2 = r2_score(y_test, y_pred)
                    adj_r2 = 1 - ((1 - r2) * (len(y_test) - 1) / (len(y_test) - len(features) - 1))
                    fig= go.Figure()
                    fig.add_trace(go.Scatter(y=y_test,mode='lines', name='Test Set'))
                    fig.add_trace(go.Scatter(y=y_pred, mode='lines', name='Predicted Set'))
                    fig.update_layout(
                        title=dict(
                            text=f'Graph of Test Set vs Prediction Set for {model_type} Model'))
                    return html.Div(
                        [html.P(f"The metrics below are based on the test set of your data for {model_type}:"),
                         html.P(f"Mean Squared Error:{mse}"), html.P(f"Root Mean Squared Error:{rmse}"),
                         html.P(f"Mean Absolute Error:{mae}"), html.P(f"R-Squared:{r2}"),
                         html.P(f"Adjusted R-Squared:{adj_r2}"), dcc.Graph(figure=fig)],style=style2,className="hover-tile"), model_base64, lt_base64, sc_base64
                else:
                    y_pred = random_search.best_estimator_.predict(x_test)
                    mse= round(mean_squared_error(y_test,y_pred),4)
                    rmse= np.sqrt(mse)
                    mae= mean_absolute_error(y_test,y_pred)
                    r2= r2_score(y_test, y_pred)
                    adj_r2= 1-((1-r2)*(len(y_test)-1)/(len(y_test)-len(features)-1))
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(y=y_test, mode='lines', name='Test Set'))
                    fig.add_trace(go.Scatter(y=y_pred, mode='lines', name='Predicted Set'))
                    fig.update_layout(
                        title=dict(
                            text=f'Graph of Test Set vs Prediction Set for {model_type} Model'))
                    return html.Div([html.P(f"The metrics below are based on the test set of your data for {model_type}:"),
                                     html.P(f"Mean Squared Error:{mse}"),html.P(f"Root Mean Squared Error:{rmse}"),
                                     html.P(f"Mean Absolute Error:{mae}"),html.P(f"R-Squared:{r2}"),
                                     html.P(f"Adjusted R-Squared:{adj_r2}"),
                                     html.Pre(f"Best Parameters for {model_type}\n {random_search.best_params_}"),
                                     dcc.Graph(figure=fig)],style=style2,className="hover-tile"), model_base64, lt_base64, sc_base64

    except:
        return "","","",""
#======================================================================================

@my_app.callback(Output('download-data-cleaned','data'),
                 [Input('radio','value'),
                  Input('store1','data'),
                  Input('btn_csv','n_clicks')], prevent_initial_call=True)
def out(value, data, n_clicks):
    if n_clicks>1:
        return ""
    if value == 'Cleaned Data' and n_clicks:
        df = pd.read_json(data, orient='table')
        return dcc.send_data_frame(df.to_csv, 'cleaned_data.csv')

@my_app.callback(Output('predout','children'),
                 [Input('store2','data'),
                  Input('store3lt','data'),
                  Input('store4sc','data'),
                  Input('in2','value'),
                  Input('btn_analyze', 'n_clicks')])
def dope(model_base64,lt,sc,row_data, n_clicks):
    try:
        if n_clicks:
            lisy = row_data.split(',')
            df = pd.DataFrame(columns=lisy)
            df.loc[0] = convert_list(lisy)  # list
            categorical_columns = df.select_dtypes(include=['object']).columns
            for i in categorical_columns:
                df[i] = LabelEncoder().fit_transform(df[i])
            x = df.values

            model_bytes= base64.b64decode(model_base64.encode("utf-8"))
            # 2. Deserialize the model (using BytesIO)
            buffer = BytesIO(model_bytes)
            trained_model = joblib.load(buffer)  # Load from bytes

            lt_bytes = base64.b64decode(lt.encode("utf-8"))
            # 2. Deserialize
            buffer2 = BytesIO(lt_bytes)
            label_tranform = joblib.load(buffer2)  # Load from bytes

            sc_bytes = base64.b64decode(sc.encode("utf-8"))
            # 2. Deserialize
            buffer3 = BytesIO(sc_bytes)
            standard_scaler = joblib.load(buffer3)  # Load from bytes

            if label_tranform is None:
                x= standard_scaler.transform(x)
                pred= trained_model.predict(x)
                return html.Div([html.Pre(f"Prediction: {pred}")])
            else:
                x = standard_scaler.transform(x)
                pred = trained_model.predict(x)
                pred= label_tranform.inverse_transform(pred)
                return html.Div([html.Pre(f"Prediction: {pred}")])
    except:
        return html.Pre(f"...No Prediction Yet...")

if __name__ == '__main__':
    my_app.run_server(
        debug = True,
        host= '0.0.0.0',
        port= 8080
    )
