import dash
from dash import html, dcc, Input, Output, State
from PIL import Image
import io, random
import base64
import dash_bootstrap_components as dbc
style= {'textAlign': 'center',
        'background':'linear-gradient(rgba(0,0,0,0.3),rgba(0,0,0,0.3)),url("https://github.com/Bravelion2017/source/blob/main/baby.jpg?raw=true")',
        'background-size':'cover','background-position':'center','height':'100vh',
        'width':'100%'}

app = dash.Dash(__name__,external_stylesheets=[dbc.themes.SUPERHERO])
server= app.server
# Compression function
def resize_and_compress_image(image_bytes, target_kb, max_width=800, max_height=800, quality_step=5, min_quality=10):
    img = Image.open(io.BytesIO(image_bytes))
    img = img.convert("RGB")

    # Resize while maintaining aspect ratio
    img.thumbnail((max_width, max_height), Image.ANTIALIAS)

    target_bytes = target_kb * 1024
    quality = 95

    while quality >= min_quality:
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=quality)
        size = buffer.tell()

        if size <= target_bytes:
            return buffer.getvalue(), quality, img.size

        quality -= quality_step

    # Save with lowest quality if needed
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=min_quality)
    return buffer.getvalue(), min_quality, img.size

app.index_string='''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>Image Compressor</title>
        <link rel="icon" href="https://github.com/Bravelion2017/source/blob/main/6326.jpg?raw=true">
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


# Layout
app.layout = html.Div([
    html.Br(),
    html.H2("Image Compressor"),

    dcc.Upload(
        id='upload-image',
        children=html.Div(['Drag and Drop or ', html.A('Select an Image')]),
        style={
            'width': '100%', 'height': '60px', 'lineHeight': '60px',
            'borderWidth': '1px', 'borderStyle': 'dashed',
            'borderRadius': '5px', 'textAlign': 'center', 'margin': '10px'
        },
        multiple=False
    ),

    html.Div(id='original-preview'),

    dcc.Input(id='target-size', type='number', placeholder='Target size in KB', style={'margin': '5px'}),
    dcc.Input(id='max-width', type='number', placeholder='Max Width (e.g. 800)', style={'margin': '5px'}),
    dcc.Input(id='max-height', type='number', placeholder='Max Height (e.g. 800)', style={'margin': '5px'}),

    html.Button('Compress Image', id='compress-btn', n_clicks=0, style={'margin': '10px'}),

    html.Div(id='output-message', style={'margin': '10px'}),
    html.Div(id='compressed-preview'),
    html.A('Download Compressed Image', id='download-link', href='', download='compressed.jpg', target='_blank'),
    html.Br(),
dcc.Markdown("Bravelion | 2025 | Contact for Interactive Web App: [email](mailto:oseme781227@gmail.com) ")
], style=style)


# Show original preview
@app.callback(
    Output('original-preview', 'children'),
    Input('upload-image', 'contents'),
    prevent_initial_call=True
)
def show_original_image(contents):
    if contents:
        return html.Div([
            html.H5("Original Image Preview:"),
            html.Img(src=contents, style={'maxWidth': '100%', 'maxHeight': '300px', 'marginBottom': '10px'})
        ])
    return ""


# Handle compression
@app.callback(
    Output('output-message', 'children'),
    Output('compressed-preview', 'children'),
    Output('download-link', 'href'),
    Input('compress-btn', 'n_clicks'),
    State('upload-image', 'contents'),
    State('target-size', 'value'),
    State('max-width', 'value'),
    State('max-height', 'value'),
    prevent_initial_call=True
)
def compress_and_show(n_clicks, contents, target_kb, max_width, max_height):
    if contents is None or target_kb is None:
        return "Please upload an image and set a target size.", "", ""

    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)

    try:
        max_width = max_width or 800
        max_height = max_height or 800

        compressed_bytes, used_quality, new_size = resize_and_compress_image(
            decoded, target_kb, max_width, max_height
        )
        b64_compressed = base64.b64encode(compressed_bytes).decode()
        href = f"data:image/jpeg;base64,{b64_compressed}"
        size_kb = len(compressed_bytes) / 1024

        msg = (f"Compressed to {size_kb:.2f} KB at quality {used_quality}. "
               f"New dimensions: {new_size[0]}x{new_size[1]}")

        preview_img = html.Div([
            html.H5("Compressed Image Preview:"),
            html.Img(src=href, style={'maxWidth': '100%', 'maxHeight': '300px', 'marginBottom': '10px'})
        ])

        return msg, preview_img, href

    except Exception as e:
        return f"Error: {str(e)}", "", ""

if __name__ == '__main__':
    my_app.run_server(
        debug = True,
        host= '0.0.0.0',
        port= 8080
    )
