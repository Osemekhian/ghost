import yt_dlp
import instaloader
import os
from urllib.parse import urlparse
import dash as dash
from dash import html, dcc, Input, Output, State, no_update
import io
import uuid
import random
import base64
import dash_bootstrap_components as dbc
import tempfile, time, re
import requests
style= {'textAlign': 'center',
        'background': 'linear-gradient(rgba(0,0,0,0.3),rgba(0,0,0,0.3)),url("https://github.com/Osemekhian/ghost/blob/main/download.gif?raw=true")',
        'background-size': 'cover', 'background-position': 'center', 'height': '100vh',
        'width': '100%','color':'black'
        }
# def download_with_yt_dlp(url):
#     ydl_opts = {
#         'format': 'bestvideo[height<=720]+bestaudio/best',
#         'outtmpl': '%(title)s.%(ext)s',
#         'quiet': False,
#     }
#     try:
#         with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#             ydl.download([url])
#     except Exception as e:
#         print(f"Error: {e}")

# def download_with_yt_dlp(url, download_dir='downloads'):
#     # Create download directory if it doesn't exist
#     os.makedirs(download_dir, exist_ok=True)
#
#     # Generate a unique filename to avoid collisions
#     unique_id = str(uuid.uuid4())[:8]
#     outtmpl = os.path.join(download_dir, f'%(title)s_{unique_id}.%(ext)s')
#
#     ydl_opts = {
#         'format': 'bestvideo[height<=720]+bestaudio/best',
#         'outtmpl': outtmpl,
#         'quiet': True,
#         'no_warnings': True,
#     }
#
#     try:
#         with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#             info_dict = ydl.extract_info(url, download=True)
#             filename = ydl.prepare_filename(info_dict)
#
#             # Get just the filename portion for the download link
#             display_name = os.path.basename(filename)
#
#             # Return both the full path and a display name
#             return {
#                 'status': 'success',
#                 'filepath': filename,
#                 'filename': display_name
#             }
#
#     except Exception as e:
#         return {
#             'status': 'error',
#             'message': str(e)
#         }

def download_youtube_video(url):
    try:
        # Create temporary directory
        with tempfile.TemporaryDirectory() as tmp_dir:
            ydl_opts = {
                'format': 'bestvideo[height<=720]+bestaudio/best[ext=mp4]',
                'outtmpl': os.path.join(tmp_dir, '%(title)s.%(ext)s'),
                'quiet': True,
                'no_warnings': True,
                'merge_output_format': 'mp4',
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info_dict)

                # Read the downloaded file
                with open(filename, 'rb') as f:
                    video_bytes = f.read()

                if len(video_bytes) == 0:
                    return None, "Downloaded video is empty"

                # Clean filename for download
                clean_title = re.sub(r'[^\w\-_\. ]', '', info_dict.get('title', 'youtube_video'))
                download_filename = f"{clean_title}_{str(uuid.uuid4())[:8]}.mp4"

                return video_bytes, download_filename

    except yt_dlp.utils.DownloadError as e:
        return None, f"YouTube error: {str(e)}"
    except Exception as e:
        return None, f"Error: {str(e)}"

# def download_instagram_video(url, output_path='.'):
#     try:
#         L = instaloader.Instaloader(dirname_pattern=output_path)
#         shortcode = url.split("/")[-2]
#         post = instaloader.Post.from_shortcode(L.context, shortcode)
#
#         if not post.is_video:
#             print("This post doesn't contain a video")
#             return
#
#         print(f"Downloading: {post.title}...")
#         L.download_post(post, target=output_path)
#         print("Download completed!")
#     except Exception as e:
#         print(f"Error: {e}")
def validate_instagram_url(url):
    """Validate various Instagram URL formats"""
    patterns = [
        r'^https?://(www\.)?instagram\.com/p/[^/]+/?',
        r'^https?://(www\.)?instagram\.com/reel/[^/]+/?',
        r'^https?://(www\.)?instagram\.com/tv/[^/]+/?',
        r'^https?://(www\.)?instagr\.am/p/[^/]+/?',
        r'^https?://(www\.)?instagr\.am/reel/[^/]+/?',
        r'^https?://(www\.)?instagr\.am/tv/[^/]+/?'
    ]
    return any(re.match(pattern, url) for pattern in patterns)


def extract_shortcode(url):
    """Extract shortcode from various Instagram URL formats"""
    parsed = urlparse(url)
    path_segments = [p for p in parsed.path.split('/') if p]

    if len(path_segments) >= 2 and path_segments[0] in ['p', 'reel', 'tv']:
        return path_segments[1]
    return None


def download_instagram_video(url):
    try:
        if not validate_instagram_url(url):
            return None, "Invalid Instagram URL. Supported formats:\n- https://www.instagram.com/p/XXXXXXX/\n- https://www.instagram.com/reel/XXXXXXX/\n- https://www.instagram.com/tv/XXXXXXX/"

        shortcode = extract_shortcode(url)
        if not shortcode:
            return None, "Could not extract post ID from URL"

        # Create temporary directory
        with tempfile.TemporaryDirectory() as tmp_dir:
            L = instaloader.Instaloader(
                dirname_pattern=tmp_dir,
                filename_pattern='{shortcode}',
                save_metadata=False,
                download_pictures=False,
                download_video_thumbnails=False
            )

            # Get post
            post = instaloader.Post.from_shortcode(L.context, shortcode)

            if not post.is_video:
                return None, "This post doesn't contain a video"

            # Download to temporary directory
            L.download_post(post, target=tmp_dir)

            # Find the downloaded video file
            for file in os.listdir(tmp_dir):
                if file.endswith('.mp4'):
                    with open(os.path.join(tmp_dir, file), 'rb') as f:
                        video_bytes = f.read()
                    return video_bytes, file

            return None, "No video file found after download"

    except instaloader.exceptions.InstaloaderException as e:
        return None, f"Instagram error: {str(e)}"
    except Exception as e:
        return None, f"An error occurred: {str(e)}"

# Example usage
# download_instagram_video("https://www.instagram.com/instagram/reel/DIRaymXsovm/?hl=en")

app= dash.Dash(__name__,external_stylesheets=[dbc.themes.SKETCHY])
#server= app.server

app.index_string='''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>Youtube-IG Downloader</title>
        <link rel="icon" href="https://github.com/Bravelion2017/source/blob/main/download.png?raw=true">
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
    html.H2("Youtube | Instagram Downloader"), html.Pre(f"by: Osemekhian Ehilen"),html.Br(),

    dcc.Tabs(id='yi', children=[
        dcc.Tab(label='YouTube Videos', value='youtube'),
        dcc.Tab(label='Instagram Videos', value='instagram'),
    ]),
    html.Div(id='out'),

    #dcc.Markdown("Bravelion | 2025 | Contact for Interactive Web App: [email](mailto:oseme781227@gmail.com) ")
], style= style)

yt_layout= html.Div([
    dbc.Input(id='in1',placeholder="Paste Link to Your YouTube Video...",type='text', size="lg", className="mb-3"),
    dbc.Button('Download', id='down1', color='primary'),
    html.Div(id='out1',style={'white-space': 'pre-line'}),
    dcc.Download(id="video-download"),
    dcc.Store(id='video-store2')
])
@app.callback(
    Output('out1','children'),
    Output('video-store2','data'),
    Input('down1','n_clicks'),
    State('in1','value'),
    prevent_initial_call= True
)
def prepare_download(n_clicks, url):
    if not url:
        return dbc.Alert("Please enter a YouTube URL", color="danger"), no_update

    if not re.match(r'^(https?\:\/\/)?(www\.)?(youtube\.com|youtu\.?be)\/.+', url):
        return dbc.Alert("Invalid YouTube URL format", color="danger"), no_update

    video_bytes, error = download_youtube_video(url)

    if not video_bytes:
        return dbc.Alert(error, color="danger"), no_update

    # Encode video bytes to base64 for storage
    video_b64 = base64.b64encode(video_bytes).decode('utf-8')
    return (
        dbc.Alert("✓ Video downloaded successfully! Your download will start automatically...", color="success"),
        {'video': video_b64, 'filename': error}
    )


@app.callback(
    Output("video-download", "data"),
    Input('video-store2', 'data'),
    prevent_initial_call=True
)
def trigger_download(data):
    if data and 'video' in data:
        time.sleep(1)  # Small delay to show status message
        video_bytes = base64.b64decode(data['video'])
        return dcc.send_bytes(video_bytes, data['filename'])

    return no_update



ig_layout = html.Div([
    dbc.Input(id='in2',placeholder="Paste Link to Your Instagram Video...",type='text', size="lg", className="mb-3"),
    dbc.Button('Download', id='down2',n_clicks=0, color='primary'),
    html.Div(id='out2',style={'white-space': 'pre-line'}),
    dcc.Download(id="video-downloader"),
    dcc.Store(id='video-store')
])
@app.callback(
    Output('out2','children'),
          Output('video-store','data'),
          Input('down2','n_clicks'),
          State('in2','value'),
          prevent_initial_call= True
)
def prepare_download(n_clicks, url):
    if not url:
        return dbc.Alert("Please enter a URL first", color="danger"), no_update

    video_bytes, error = download_instagram_video(url)

    if not video_bytes:
        return dbc.Alert(f"Error: {error}", color="danger"), no_update

    # Encode video bytes to base64 for storage
    video_b64 = base64.b64encode(video_bytes).decode('utf-8')

    return (
        dbc.Alert("Video downloaded successfully! Your download will start automatically...", color="success"),
        {'video': video_b64, 'filename': error}  # Using 'error' which contains the filename
    )


@app.callback(
    Output("video-downloader", "data"),
    Input('video-store', 'data'),
    prevent_initial_call=True
)
def trigger_download(data):
    if data and 'video' in data:
        time.sleep(1)  # Small delay to show status message
        video_bytes = base64.b64decode(data['video'])
        filename = data.get('filename', 'instagram_video.mp4')

        # Clean filename
        filename = re.sub(r'[^\w\-_.]', '_', filename)
        if not filename.endswith('.mp4'):
            filename += '.mp4'

        return dcc.send_bytes(video_bytes, filename)

    return no_update



@app.callback(
    Output('out','children'),
    Input('yi','value')
)
def updater(tab):
    if tab == 'youtube':
        return yt_layout
    if tab == 'instagram':
        return ig_layout

if __name__ == '__main__':
    app.run(
        debug=False,
        host= '127.0.0.1',
        port= random.randint(8000,9999)
    )