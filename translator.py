import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
from googletrans import Translator, LANGUAGES
import random

# Initialize translator
translator = Translator()

# External stylesheets for Bootstrap
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX])
server = app.server
LANGUAGES = {name.title(): code for code, name in LANGUAGES.items()}
app.index_string='''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>Translator</title>
        <link rel="icon" href="https://raw.githubusercontent.com/Osemekhian/ghost/refs/heads/main/%E2%80%94Pngtree%E2%80%94translating%20icon%20simple%20style_5166057.png">
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
            <footer style="text-align:center; padding:20px; background:#f2f2f2;">
            <p>Bravelion© 2025 | All rights reserved | Contact for Interactive Web App: <a href="mailto:oseme781227@gmail.com">email</a></p>
        </footer>
    </body>
</html>
'''

# App layout
app.layout = dbc.Container([
    html.H2("🌍 Smart Translator", className="text-center mt-4 mb-3"),

    dbc.Row([
        dbc.Col([
            dbc.Label("From Language"),
            dcc.Dropdown(
                options=[{"label": k, "value": v} for k, v in LANGUAGES.items()],
                value='en',
                id='source-lang',
                className="mb-3",
                style={"fontSize": "1rem"}
            )
        ], xs=12, md=6),

        dbc.Col([
            dbc.Label("To Language"),
            dcc.Dropdown(
                options=[{"label": k, "value": v} for k, v in LANGUAGES.items()],
                value='fr',
                id='target-lang',
                className="mb-3",
                style={"fontSize": "1rem"}
            )
        ], xs=12, md=6),
    ]),

    dbc.Textarea(
        id='input-text',
        placeholder="Type or paste text to translate...",
        style={"height": "150px", "fontSize": "1.1rem"},
        className="mb-3"
    ),

    dbc.Button("Translate", id='translate-btn', color="primary", size="lg", className="w-100 mb-3"),

    dbc.Card([
        dbc.CardHeader("Translated Text", className="bg-light text-dark"),
        dbc.CardBody([
            html.Div(id='translated-output', style={"fontSize": "1.2rem"})
        ])
    ], className="shadow")
], fluid=True, style={"maxWidth": "800px", "margin": "auto"})


# Callback for translation
@app.callback(
    Output('translated-output', 'children'),
    Input('translate-btn', 'n_clicks'),
    State('input-text', 'value'),
    State('source-lang', 'value'),
    State('target-lang', 'value'),
)
def translate_text(n, text, src_lang, tgt_lang):
    if not n or not text:
        return ""
    try:
        translated = translator.translate(text, src=src_lang, dest=tgt_lang)
        return translated.text
    except Exception as e:
        return f"⚠️ Error: {str(e)}"


if __name__ == "__main__":
    app.run(
        debug=False,
        port=random.randint(8000, 9999),  # 8080
        host="127.0.0.1"
    )
