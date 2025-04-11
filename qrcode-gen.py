import dash
from dash import dcc, html, Input, Output, State
import qrcode, random
from io import BytesIO
import base64
import dash_bootstrap_components as dbc

app = dash.Dash(__name__,external_stylesheets=[dbc.themes.QUARTZ])
app.title= "QR-Code Generator"

app.index_string='''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>QR-Code Generator</title>
        <link rel="icon" href="https://github.com/Bravelion2017/source/blob/main/qr_code.png?raw=true">
        {%css%}
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


app.layout = html.Div([
    html.Br(),
    html.H1("QR Code Generator", style={'textAlign': 'center'}),

    html.Div([
        dcc.Input(
            id='url-input',
            type='text',
            placeholder='Enter URL here...',
            style={'width': '80%', 'height': '40px', 'fontSize': '16px'}
        ),
        html.Button(
            'Generate QR Code',
            id='generate-button',
            n_clicks=0,
            style={'height': '40px', 'marginLeft': '10px'}
        )
    ], style={'display': 'flex', 'justifyContent': 'center', 'margin': '20px'}),

    html.Div(id='qr-code-container', style={'textAlign': 'center', 'margin': '20px'}),

    html.Div(id='download-container', style={'textAlign': 'center'}),
    html.Div(dcc.Markdown("Bravelion | 2025 | Contact for Interactive Web App: [email](mailto:oseme781227@gmail.com) "), style={'textAlign': 'center'})
])


@app.callback(
    Output('qr-code-container', 'children'),
    Output('download-container', 'children'),
    Input('generate-button', 'n_clicks'),
    State('url-input', 'value')
)
def generate_qr_code(n_clicks, url):
    if n_clicks == 0 or not url:
        return None, None

    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # Convert image to bytes
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()

    # Create download link
    download_link = html.A(
        'Download QR Code',
        id='download-link',
        download="qr_code.png",
        href=f"data:image/png;base64,{img_str}",
        style={
            'display': 'inline-block',
            'padding': '10px 20px',
            'backgroundColor': '#007BFF',
            'color': 'white',
            'textDecoration': 'none',
            'borderRadius': '5px',
            'marginTop': '20px'
        }
    )

    # Display QR code image
    qr_code = html.Img(
        src=f"data:image/png;base64,{img_str}",
        style={'maxWidth': '300px', 'border': '1px solid #ddd', 'padding': '10px'}
    )

    return qr_code, download_link


if __name__ == '__main__':
    app.run(
        debug=False,
        port=random.randint(8000, 9999),  # 8080
        host="127.0.0.1",
    )