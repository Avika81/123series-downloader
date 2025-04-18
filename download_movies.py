from pathlib import Path

from downloader import DownloadVideos
from get_download_link import GetDownloadLink
from my_series import MOVIES

MOVIES_PATH = Path(__file__).parent / "movies"


def main():
    gvl = GetDownloadLink()
    dvs = DownloadVideos()
    for url in MOVIES:
        try:
            name = f'{MOVIES_PATH / url.split("/movie/")[1].rsplit("-", 1)[0]}.mp4'
            if Path(name).exists():
                continue

            dvs.add((name, gvl.get_download_link(url)))
        except Exception:
            print(f"Error downloading {url}")

    gvl.driver.quit()
    dvs.wait_for_downloads()


if __name__ == "__main__":
    main()
