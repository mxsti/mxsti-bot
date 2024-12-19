""" utility for downloading video/audio from youtube """

import os
import yt_dlp
from utils.exceptions import DownloadFailedError


async def download_audio(url):
    """
    Utilizes yt_dlp to download audio from given url

    Parameters:
        url - url of the youtube video that should be downloaded

    Returns:
        title and id of the youtube video
    """
    # options/config for download
    ydl_opts = {
        'format': 'm4a/bestaudio/best',
        'postprocessors': [{  # Extract audio using ffmpeg (needs to be installed)
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'm4a',
        }],
        'paths': {'home': f'{os.getcwd()}/audio'},
        'writethumbnail': 'true',  # also save thumbnail cause why not

    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # also downloads video/audio file
            video_info = ydl.extract_info(url)
    except Exception as e:
        raise DownloadFailedError(e.args) from e

    return [video_info["id"], video_info["title"]]
