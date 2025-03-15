from pathlib import Path
import subprocess
import json
import sys

from get_download_links import get_links_file_path

DOWNLOAD_LINE = 'yt-dlp -N 2 -q --retry-sleep 5 -o "{name}" "{url}" '


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

    def start_downloads(
        self,
    ):
        processes = []
        for name, url in self.to_download.items():
            if not Path(self.get_filename(name)).exists():
                processes.append(
                    subprocess.Popen(
                        DOWNLOAD_LINE.format(url=url, name=self.get_filename(name)),
                        shell=True,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                )
        return processes


if __name__ == "__main__":
    # usage: python download_videos.py <serie_name>
    DownloadVideos(sys.argv[1]).start_downloads()
