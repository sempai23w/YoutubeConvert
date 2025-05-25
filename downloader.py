import os
import sys
import yt_dlp
from pydub import AudioSegment

# Função para baixar vídeo em MP4
def download_mp4(url, output_path):
    print(f"[LOG] Iniciando download MP4 (yt-dlp): {url}", file=sys.stderr)
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4',
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        'merge_output_format': 'mp4',
        'quiet': True,
        'noplaylist': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        print(f"[LOG] Download MP4 concluído: {filename}", file=sys.stderr)
        return filename

# Função para baixar áudio em MP3
def download_mp3(url, output_path):
    print(f"[LOG] Iniciando download MP3 (yt-dlp): {url}", file=sys.stderr)
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        'quiet': True,
        'noplaylist': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = os.path.splitext(ydl.prepare_filename(info))[0] + '.mp3'
        print(f"[LOG] Download MP3 concluído: {filename}", file=sys.stderr)
        return filename