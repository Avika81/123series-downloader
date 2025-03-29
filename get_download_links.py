from pathlib import Path
import selenium
from seleniumwire import webdriver
from seleniumwire.inspect import TimeoutException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

from save_to_json import add_video
from series import *

URL_TEMPLATE = "https://123series.art/series/{name}/{season}-{episode}/"
MAX_EPISODE = 400  # more than this and you should not watch this serie


class EpisodeDoesNotExist(Exception):
    pass


class DidNotFindDownloadLink(Exception):
    pass


class GetVideoLinks:
    def __init__(self):
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    def _wait_for_download_url(self):
        return self.driver.wait_for_request(
            "index-v1-a1.m3u8|(?=.*lightningbolts)(?=.*m3u8)", timeout=15
        )

    def _try_all_servers(self, url):
        window_handle = self.driver.window_handles[0]
        for _ in range(3):
            for nav in self.driver.find_element(By.ID, "list_of").find_elements(
                By.CLASS_NAME, "nav-item"
            ):
                self.driver.switch_to.window(window_handle)
                self.driver.execute_script("arguments[0].click();", nav)
                self.driver.execute_script(
                    "arguments[0].click();",
                    nav.find_element(By.XPATH, "//a[@href='javascript:;']"),
                )
                try:
                    nav.click()
                except selenium.common.exceptions.ElementClickInterceptedException:
                    print(f"Got an extremely annoying add, reloading the page")
                    self.driver.get(url)
                    break
                try:
                    return self._wait_for_download_url()
                except TimeoutException:
                    continue
        # It does not exist on all the servers
        raise DidNotFindDownloadLink(f"all the servers for {url} does not work :/")

    def get_download_link(self, url):
        del self.driver.requests  # clean old requests.
        self.driver.get(url)
        if not self.driver.find_elements(By.ID, "main-wrapper"):
            raise EpisodeDoesNotExist(f"{url} has no presentation of video :/")
        try:
            return self._wait_for_download_url()
        except TimeoutException:
            print(f"Error downloading: {url}, Checing if other server works :/")
            return self._try_all_servers(url)


def get_filename(serie, season, episode):
    return (
        Path(__file__).parent
        / "series"
        / serie.human_name
        / f"{season:02}-{episode:02}.mp4"
    )


def add_episode(serie, season, gvl, episode):
    add_video(
        serie_name=serie.human_name,
        name=get_filename(serie=serie, season=season, episode=episode),
        url=gvl.get_download_link(
            URL_TEMPLATE.format(name=serie.name, season=season, episode=episode)
        ),
    )


def get_season_links(serie: Serie, season: int, gvl: GetVideoLinks):
    for episode in range(1, MAX_EPISODE):
        try:
            add_episode(serie=serie, season=season, gvl=gvl, episode=episode)
        except EpisodeDoesNotExist:
            break
        except Exception as e:
            # Problem with specific episode, log and try the next one :)
            print(
                f"Error - {repr(e)}, trying to download {serie.human_name}:{season}-{episode}"
            )
            continue


if __name__ == "__main__":
    # Tests:
    serie = SUITS
    gvl = GetVideoLinks()
    # get_season_links(gvl=gvl, serie=serie, season=7)
    for season in range(1, 12):
        get_season_links(gvl=gvl, serie=serie, season=season)
    gvl.driver.quit()
