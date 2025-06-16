# libraries import
import dash as dash
from dash import dcc,dash_table, State, no_update
import joblib, base64, random, io, os,uuid
from io import BytesIO
from dash import html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from gtts import gTTS
import pdfplumber
import requests
import tempfile
style= {'textAlign': 'center',
        'color':'#485785'}
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
marks= lambda min,max:{i:f"{i}" for i in range(min,max)}

# helper function
# Function to test internet connectivity
def check_internet():
    try:
        requests.get("https://www.google.com", timeout=5)
        return True
    except requests.ConnectionError:
        return False
uid= str(uuid.uuid4())[:5]
# The App
app= dash.Dash(__name__,external_stylesheets=[dbc.themes.MORPH],suppress_callback_exceptions=True) #dbc.themes.MORPH | dbc.themes.SKETCHY
# server= app.server

app.index_string='''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>PDF To Audio</title>
        <link rel="icon" href="6326.jpg">
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

app.layout= html.Div([
    html.Br(),
    html.H1("PDF/Text To Speech"),
    html.Pre("...transform your pdf book into audio format..."),
    html.Br(),
html.Div([dcc.Upload(id='upload-pdf',children=html.Div(['Drag and Drop or ',html.A('Select PDF File')]),accept='application/pdf',style={
        'width': '50%','height': '60px','lineHeight': '60px','borderWidth': '1px','borderStyle': 'dashed',
        'borderRadius': '5px','textAlign': 'center','background-color':'#485785','color':'white',
        'align-items':'center','margin':'auto'})]),
    html.Pre(f'or add text below:'),
    dbc.Input(id="in1", placeholder="Paste Your Text/Write-up Here...", type='textarea',
              size="lg", className="mb-3",style={'height':'150px','fontSize':'20px',
                                                 'width':'800px','margin':'0 auto','display':'block'}),
    html.Div(id='out'),
    dcc.Loading(
            id="loading",
            type="circle",
            children=html.Div(id='output-status', className="mt-3 text-center")
        ),
    html.Div(id='download-container', className='mt-3 text-center'),
    dcc.Store(id='audio-store'),
    dcc.Download(id='download-audio')

], style=style)

@app.callback(
    Output('out', 'children'),
    Input('upload-pdf','contents'),
    prevent_initial_call= True
)
def updater(contents):
    if contents is None:
        return html.P('No PDF Uploaded yet.')
    content_type, content_string = contents.split(',')
    if 'application/pdf' not in content_type:
        return html.P('Please upload a valid PDF file.')
    pdf_data= f"data:application/pdf;base64,{content_string}"
    return html.Iframe(src= pdf_data ,style={'width':'70%','height':'500px',
                                             'border':'2px solid #ccc','borderRadius':'8px',
                                             'boxShadow':'0 4px 8px rgba(0,0,0,0.1)',
                                             'margin':'20px auto','display':'block'})


@app.callback(
    [
        Output('output-status', 'children'),
        Output('audio-store', 'data'),
        Output('download-container', 'children')
    ],
    Input('upload-pdf', 'contents'),
    State('upload-pdf', 'filename'),
    Input('in1', 'value'),
    prevent_initial_call=True
)
def process_pdf(contents, filename,input_txt):
    if (contents is None) and (input_txt is None):
        return "No file uploaded.", None, no_update

    try:
        if contents:
            # Decode the uploaded PDF (base64 to bytes)
            content_type, content_string = contents.split(',')
            decoded_pdf = base64.b64decode(content_string)

            # Use BytesIO to handle the PDF in memory
            pdf_buffer = io.BytesIO(decoded_pdf)

            # Extract text using pdfplumber
            with pdfplumber.open(pdf_buffer) as pdf:
                text = ''
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text
        else:
            text = input_txt
            filename=f'audio_generated_{uid}.txt'

        if not text.strip():
            return "No text could be extracted from the PDF.", None, no_update

        # Initialize audio buffer
        audio_buffer = io.BytesIO()
        source = "gTTS"

        # Try gTTS first
        try:
            if not check_internet():
                raise ConnectionError("No internet connection detected.")

            tts = gTTS(text=text, lang='en', slow=False, tld='us')
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)

            # Check if audio buffer has meaningful content
            audio_data = audio_buffer.read()
            audio_buffer.seek(0)
            if len(audio_data) < 1024:  # Arbitrary threshold for valid MP3
                raise ValueError("Generated audio is too small, likely invalid.")

        except Exception as e:
            # Fallback to saving a temporary file for debugging
            print(f"gTTS failed: {str(e)}. Saving to temporary file for debugging.")
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
                tts = gTTS(text=text, lang='en', slow=False, tld='us')
                tts.save(temp_file.name)
                with open(temp_file.name, 'rb') as f:
                    audio_data = f.read()
                audio_buffer = io.BytesIO(audio_data)
                audio_buffer.seek(0)
                temp_file_path = temp_file.name

        # Encode audio buffer to base64 for storage
        audio_base64 = base64.b64encode(audio_buffer.read()).decode('utf-8')
        audio_buffer.seek(0)  # Reset for download
        # audio_buffer.close()
        # pdf_buffer.close()

        # Clean up temporary file if created
        if 'temp_file_path' in locals():
            try:
                os.unlink(temp_file_path)
            except:
                pass

        # Create download link
        download_filename = os.path.splitext(filename)[0] + ".mp3"


        return (
            f"Audio generated successfully for {filename} using {source}!",
            audio_base64,
            html.A(
                dbc.Button("Download MP3", color="success"),
                id='download-link',
                download=download_filename,
                className="mt-2"
            )
        )

    except Exception as e:
        return f"Error: {str(e)}", None, no_update


# Callback to trigger download when the button is clicked
@app.callback(
    Output('download-audio', 'data'),
    Input('download-link', 'n_clicks'),
    State('audio-store', 'data'),
    State('upload-pdf', 'filename'),
    prevent_initial_call=True
)
def trigger_download(n_clicks, audio_base64, filename):
    if filename is None:
        filename=f'audio_generated_{uid}.txt'
    if n_clicks and audio_base64:
        download_filename = os.path.splitext(filename)[0] + ".mp3"
        return {
            'content': audio_base64,
            'filename': download_filename,
            'base64': True
        }
    return no_update

#======================================================================================================
if __name__ == "__main__":
    app.run(
        debug=False,
        port=random.randint(8000, 9999),  # 8080
        host="127.0.0.1"
    )
