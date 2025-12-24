from pathlib import Path
from selenium.common.exceptions import NoSuchWindowException
from selenium.webdriver.common.by import By
from download_series import SerieDownloader
from downloader import async_download_file_from_url
from get_download_link import DownloadLinkDoesNotExist
from my_series import *

URL_TEMPLATE = "https://9animetv.to/watch/{name}?ep={episode}"
START = 1000
END = 1200


class AnimmeDownloader(SerieDownloader):
    def __init__(self, serie):
        super().__init__(serie=serie)
        self._episode_to_link = {}
        self.gvl.driver.get(
            url=URL_TEMPLATE.split("?ep=")[0].format(name=self.serie.name)
        )
        for i in range(1, int(END / 100) + 1):
            episodes_page = self.gvl.driver.find_element(By.ID, f"episodes-page-{i}")
            for n, episode in enumerate(episodes_page.children()):  # type: ignore
                self._episode_to_link[(i - 1) * 100 + n + 1] = episode.get_property(
                    "href"
                )

    def get_episode_link(self, season, episode):
        return self._episode_to_link[episode]

    def get_filename(self, season, episode, extension="mp4"):
        name = (
            Path(__file__).parent
            / "series"
            / self.serie.human_name
            / f"{episode}.{extension}"
        )
        if not name.parent.exists():
            name.parent.mkdir(parents=True)
        return name

    def download_subtitles(self, season, episode):
        name = self.get_filename(season=season, episode=episode, extension="vtt")
        if not name.exists():
            subtitles_link = self.gvl.get_subtitles_link(self._episode_to_link[episode])
            if subtitles_link:
                async_download_file_from_url(subtitles_link, name)
            else:
                print(
                    f"Error - subtitles was not found for - {self.serie.human_name} : {season}-{episode} :("
                )

    def download_episode(self, season, episode):
        name = self.get_filename(season=season, episode=episode)
        if name.exists():
            # No need to download twice
            return
        self.dvs.add(
            (name, self.gvl.get_download_link(self._episode_to_link[episode])),
        )
        print(f"Added: {self.serie.human_name} - {season}:{episode}")

    def download_all(self):
        for episode in range(START, END):
            try:
                self.download_subtitles(episode=episode, season=None)
                self.download_episode(episode=episode, season=None)
            except DownloadLinkDoesNotExist:
                if episode == 1:
                    return self.exit()
                break
            except NoSuchWindowException:
                print("An error accured")
                return self.exit()
            except Exception as e:
                print(
                    f"AAAAAAAAAAAAAAAAA: did not found a link for {self.serie.human_name} - {episode}, exception: {str(e)}"
                )
                continue
        return self.exit()

    def exit(self):
        self.dvs.wait_for_downloads()


def main():
    for _ in range(3):
        for anime in ANIMES:
            AnimmeDownloader(anime).download_all()
    # sync_all_series()


if __name__ == "__main__":
    main()
