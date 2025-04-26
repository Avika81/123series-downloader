from pathlib import Path

from downloader import DownloadVideos, async_download_file_from_url
from get_download_link import GetDownloadLink
from my_series import MOVIES

MOVIES_PATH = Path(__file__).parent / "movies"


def main():
    gvl = GetDownloadLink()
    dvs = DownloadVideos()
    for url in MOVIES:
        try:
            name = (
                str(
                    MOVIES_PATH / url.split("/movie")[1].split("/")[1].rsplit("-", 1)[0]
                )
                + ".mp4"
            )
            if not Path(name).exists():
                dvs.add((name, gvl.get_download_link(url)))

            subtitle_name = (
                str(
                    MOVIES_PATH / url.split("/movie")[1].split("/")[1].rsplit("-", 1)[0]
                )
                + ".vtt"
            )

            if not Path(subtitle_name).exists():
                async_download_file_from_url(gvl.get_subtitles_link(url), subtitle_name)

        except Exception:
            print(f"Error downloading {url}")

    dvs.wait_for_downloads()


if __name__ == "__main__":
    main()
