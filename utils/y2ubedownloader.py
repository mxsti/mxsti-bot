import json
import yt_dlp

URL = 'https://www.youtube.com/watch?v=zd9pOoICt34'

ydl_opts = {
    'format' : 'm4a/bestaudio/best',
    'outtmpl': {'default' : 'test.m4a' }
}
with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download(URL)
