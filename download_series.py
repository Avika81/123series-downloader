from pathlib import Path
import threading

from downloader import DownloadVideos, download_file_from_url
from get_download_link import DownloadLinkDoesNotExist, GetDownloadLink
from my_series import *

URL_TEMPLATE = "https://123series.art/series/{name}/{season}-{episode}/"
# more than this and you should not watch this serie
MAX_EPISODE = 400
MAX_SEASON = 30


def get_filename(serie, season, episode, extension="mp4"):
    return (
        Path(__file__).parent
        / "series"
        / serie.human_name
        / f"{season:02}"
        / f"{season:02}-{episode:02}.{extension}"
    )


class SerieDownloader:
    def __init__(self, serie):
        self.gvl = GetDownloadLink()
        self.dvs = DownloadVideos()
        self.serie = serie
        self.subtitle_downloads = []

    def download_subtitles(self, season, episode):
        name = get_filename(
            serie=self.serie, season=season, episode=episode, extension="vtt"
        )
        if not name.exists():
            subtitles_link = self.gvl.get_subtitles_link(
                URL_TEMPLATE.format(
                    name=self.serie.name, season=season, episode=episode
                )
            )
            if subtitles_link:
                subtitle_downloader = threading.Thread(
                    target=download_file_from_url,
                    args=(subtitles_link, name),
                )
                subtitle_downloader.start()
                self.subtitle_downloads.append(subtitle_downloader)

            else:
                print(
                    "Error - subtitles was not found :/ - debug if you want, exit() to continue.. \n\n\n"
                )
                import IPython

                IPython.embed()

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
                    self.download_subtitles(episode=episode, season=season)
                    self.download_episode(episode=episode, season=season)
                except DownloadLinkDoesNotExist:
                    if episode == 1:
                        return self.exit()
                    break
                except Exception as e:
                    print(
                        f"AAAAAAAAAAAAAAAAA: did not found a link for {self.serie.human_name} - {season}:{episode}, exception: {str(e)}"
                    )
                    continue
        return self.exit()

    def exit(self):
        self.gvl.driver.quit()
        self.dvs.wait_for_downloads()
        for t in self.subtitle_downloads:
            t.join()


def main():
    for _ in range(3):
        for serie in SERIES:
            SerieDownloader(serie).download_all()


if __name__ == "__main__":
    main()
