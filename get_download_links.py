import time
from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import json
from selenium.webdriver.common.by import By

from consts import get_links_file_path
from series import *

URL_TEMPLATE = "https://123series.art/series/{name}/{season}-{episode}/"
MAX_EPISODE = 400  # more than this and you should not watch this serie


def add_video(serie_name, name, url):
    with open(get_links_file_path(serie_name)) as f:
        to_download = json.load(f)

    to_download[name] = url
    with open(get_links_file_path(serie_name), "w") as f:
        json.dump(to_download, f, indent=4)


class EpisodeDoesNotExist(Exception):
    pass


class GetVideoLinks:
    def __init__(self):
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    def get_download_link(self, url):
        del self.driver.requests  # clean old requests.
        self.driver.get(url)
        if self.driver.find_elements(By.ID, "main-wrapper"):
            try:
                return self.driver.wait_for_request("index-v1-a1.m3u8", timeout=30).url
            except Exception:
                print(f"Error downloading: {url}, cChecing if other server works :/")
                for nav in self.driver.find_element(By.ID, "list_of").find_elements(
                    By.CLASS_NAME, "nav-item"
                ):
                    for _ in range(3):
                        self.driver.execute_script("arguments[0].click();", nav)
                        self.driver.execute_script(
                            "arguments[0].click();",
                            nav.find_element(By.XPATH, "//a[@href='javascript:;']"),
                        )
                    nav.click()
                    time.sleep(15)
                return self.driver.wait_for_request("index-v1-a1.m3u8", timeout=1).url
        else:
            raise EpisodeDoesNotExist(f"{url} has no presentation of video :/")


def get_season_links(serie: Serie, season: int, gvl: GetVideoLinks):
    for episode in range(1, MAX_EPISODE):
        try:
            add_video(
                serie_name=serie.human_name,
                name=f"{season}-{episode}",
                url=gvl.get_download_link(
                    URL_TEMPLATE.format(name=serie.name, season=season, episode=episode)
                ),
            )
        except EpisodeDoesNotExist:
            break
        except Exception as e:
            # Problem with specific episode, log and try the next one :)
            print(
                f"Error - {repr(e)}, trying to download {serie.human_name}:{season}-{episode}"
            )
            continue


def download(serie):
    # start downloading the serie
    from download_videos import DownloadVideos

    DownloadVideos(serie.human_name).start_downloads()


if __name__ == "__main__":
    # Tests:
    serie = SUITS
    gvl = GetVideoLinks()
    # get_season_links(gvl=gvl, serie=serie, season=7)
    for season in range(1, 12):
        get_season_links(gvl=gvl, serie=serie, season=season)
    gvl.driver.quit()

    # download(serie)
