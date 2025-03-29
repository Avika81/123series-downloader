from concurrent.futures import ThreadPoolExecutor
import sys
import yt_dlp
from save_to_json import read_links

# debug command lines: (using the yt_dlp library instead)
# DOWNLOAD_LINE = 'yt-dlp -f best --limit-rate 50K --concurrent-fragments 4 --buffer-size 16M --downloader aria2c --downloader-args "-x 16 -k 50K" -q -c -o "{name}" "{url}" '
# DOWNLOAD_LINE = 'yt-dlp -f bestvideo+bestaudio --merge-output-format mp4 --downloader aria2c --downloader-args "aria2c:-x 16 -s 16 -k 1M" -o "{name}" "{url}"'
# DOWNLOAD_LINE = 'ffmpeg -i "{url}" -c copy "{name}"'


def download(name, req):
    options = {
        "outtmpl": name,  # Output filename format
        "merge_output_format": "mp4",  # Merge video and audio into MKV
        "http_headers": req.headers,
        "quiet": True,
    }

    with yt_dlp.YoutubeDL(options) as ydl:
        ydl.download([req.url])


class DownloadVideos:
    def __init__(self, serie_name=None, to_download=None):
        assert not (
            serie_name and to_download
        ), "can not use both `serie_name` and `to_download`"
        if serie_name:
            self.to_download = read_links(serie_name)
        if to_download:
            self.to_download = to_download

    def start_downloads(
        self,
    ):
        with ThreadPoolExecutor(max_workers=16) as executor:
            executor.map(lambda args: download(*args), list(self.to_download.items()))


if __name__ == "__main__":
    # usage: python download_videos.py <serie_name>
    DownloadVideos(sys.argv[1]).start_downloads()
