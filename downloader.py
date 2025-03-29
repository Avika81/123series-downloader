from concurrent.futures import ThreadPoolExecutor
import yt_dlp


def download(name, req):
    options = {
        "outtmpl": str(name),  # Output filename format
        "merge_output_format": "mp4",  # Merge video and audio into MKV
        "http_headers": req.headers,
        "quiet": True,
    }

    with yt_dlp.YoutubeDL(options) as ydl:
        ydl.download([req.url])


class DownloadVideos:
    def __init__(self, to_download=None):
        self.to_download = to_download

    def start_downloads(
        self,
    ):
        with ThreadPoolExecutor(max_workers=16) as executor:
            executor.map(lambda args: download(*args), list(self.to_download.items()))
