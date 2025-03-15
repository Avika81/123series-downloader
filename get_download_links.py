import time
from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import json
from pathlib import Path
from selenium.webdriver.common.by import By

from series import *

URL_TEMPLATE = "https://123series.art/series/{name}/{season}-{episode}/"
MAX_EPISODE = 400  # more than this and you should not watch this serie


def get_links_file_path(serie_name):
    path = Path(__file__).parent / "links" / f"{serie_name}.json"
    if not path.is_file():
        with open(path, "w") as f:
            json.dump({}, f, indent=4)
    return path


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

    def get_download_links(self, url):
        self.driver.get(url)
        if self.driver.find_elements(By.ID, "main-wrapper"):
            time.sleep(3)
            for request in self.driver.requests:
                if "index-v1-a1.m3u8" in request.url:
                    # maybe there is more than 1?
                    ret = request.url
            # I want the last one, the other are bad for your health
            yield ret
        else:
            raise EpisodeDoesNotExist(f"{url} has no presentation of video :/")


def get_season_links(serie: Serie, season: int, gvl: GetVideoLinks):
    for episode in range(1, MAX_EPISODE):
        try:
            for link in gvl.get_download_links(
                URL_TEMPLATE.format(name=serie.name, season=season, episode=episode)
            ):
                add_video(
                    serie_name=serie.human_name, name=f"{season}-{episode}", url=link
                )
                break
                #TODO: support more than 1 link...
        except EpisodeDoesNotExist:
            break


if __name__ == "__main__":
    ## run stuffs :)
    gvl = GetVideoLinks()
    for season in range(1, 10):
        get_season_links(THE_BLACKLIST, season=season)
    gvl.driver.quit()
