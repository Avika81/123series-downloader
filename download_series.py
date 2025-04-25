from pathlib import Path
import time
from downloader import DownloadVideos
from get_download_link import DownloadLinkDoesNotExist, GetDownloadLink
from my_series import *

URL_TEMPLATE = "https://123series.art/series/{name}/{season}-{episode}/"
# more than this and you should not watch this serie
MAX_EPISODE = 400
MAX_SEASON = 30


def get_filename(serie, season, episode):
    return (
        Path(__file__).parent
        / "series"
        / serie.human_name
        / f"{season:02}"
        / f"{season:02}-{episode:02}.mp4"
    )


class SerieDownloader:
    def __init__(self, serie):
        self.gvl = GetDownloadLink()
        self.dvs = DownloadVideos()
        self.serie = serie

    def download_episode(self, season, episode):
        name = get_filename(serie=self.serie, season=season, episode=episode)
        if name.exists():
            # No need to download twice
            return
        if not name.parent.exists():
            name.parent.mkdir(parents=True)
        self.dvs.add(
            (
                name,
                self.gvl.get_download_link(
                    URL_TEMPLATE.format(
                        name=self.serie.name, season=season, episode=episode
                    )
                ),
            )
        )
        print(f"Added: {self.serie.human_name} - {season}:{episode}")

    def download_all(self):
        for season in range(1, MAX_SEASON):
            for episode in range(1, MAX_EPISODE):
                try:
                    self.download_episode(episode=episode, season=season)
                except DownloadLinkDoesNotExist:
                    if episode == 1:
                        return self.exit()
                    break
                except Exception as e:
                    print(
                        f"AAAAAAAAAAAAAAAAA: did not found a link for {self.serie.human_name} - {season}:{episode} :("
                    )
                    continue
        return self.exit()

    def exit(self):
        self.gvl.driver.quit()
        self.dvs.wait_for_downloads()
        time.sleep(5)


def main():
    for _ in range(3):
        for serie in SERIES:
            SerieDownloader(serie).download_all()


if __name__ == "__main__":
    main()
