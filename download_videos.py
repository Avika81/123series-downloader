from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import subprocess
import json
import sys

from consts import get_links_file_path

# DOWNLOAD_LINE = 'yt-dlp -f best --limit-rate 50K --concurrent-fragments 4 --buffer-size 16M --downloader aria2c --downloader-args "-x 16 -k 50K" -q -c -o "{name}" "{url}" '
# DOWNLOAD_LINE = 'yt-dlp -f bestvideo+bestaudio --merge-output-format mp4 --downloader aria2c --downloader-args "aria2c:-x 16 -s 16 -k 1M" -o "{name}" "{url}"'
DOWNLOAD_LINE = 'ffmpeg -i "{url}" -c copy "{name}"'


class DownloadVideos:
    def __init__(self, serie_name):
        self.serie_name = serie_name

        with open(get_links_file_path(self.serie_name)) as f:
            self.to_download = json.load(f)
        self.output_dir = Path(__file__).parent / "series" / self.serie_name
        if not self.output_dir.is_dir():
            self.output_dir.mkdir()

    def get_filename(self, name):
        return self.output_dir / f"{name}.mp4"

    def run_command(self, cmd):
        p = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        print(f"Downloading: {cmd}")
        p.wait()

    def start_downloads(
        self,
    ):
        commands = [
            DOWNLOAD_LINE.format(url=url, name=self.get_filename(name))
            for name, url in self.to_download.items()
            if not Path(self.get_filename(name)).exists()
        ]

        with ThreadPoolExecutor(max_workers=16) as executor:
            executor.map(self.run_command, commands)


if __name__ == "__main__":
    # usage: python download_videos.py <serie_name>
    DownloadVideos(sys.argv[1]).start_downloads()
