import os
import yt_dlp

async def download_audio(URL):
    ydl_opts = {
        'format' : 'm4a/bestaudio/best',
        'paths': {'home' : f'{os.getcwd()}/audio'},
        'writethumbnail': 'true',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        video_info = ydl.extract_info(URL) # also downloads video/audio file

    return [video_info["id"], video_info["title"]]
