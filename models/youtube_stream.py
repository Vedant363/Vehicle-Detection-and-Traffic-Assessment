import yt_dlp
import re

global_video_id = None

YOUTUBE_URL_REGEX = r'^https:\/\/www\.youtube\.com\/watch\?v=[\w-]{11}(&t=\d+s)?$'

def initialize_youtube_stream(video_id):
    video_url = f'https://www.youtube.com/watch?v={video_id}'
    return get_youtube_stream_url(video_url)

# Function to validate the YouTube URL
def is_valid_youtube_url(youtube_url):
    return bool(re.match(YOUTUBE_URL_REGEX, youtube_url))

def get_youtube_stream_url(video_url):
    ydl_opts = {
        'format': 'best',
        'noplaylist': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=False)
        return info['url']

def extract_video_id(url):
    if 'v=' in url:
        return url.split('v=')[1].split('&')[0]
    elif 'youtu.be/' in url:
        return url.split('youtu.be/')[1]
    return None