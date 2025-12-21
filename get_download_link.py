import logging
import subprocess
import sys
import time
import selenium
import seleniumwire.request
import seleniumwire.undetected_chromedriver as webdriver

# replace with above if undetected is not your thing
# from seleniumwire import webdriver
from seleniumwire.inspect import TimeoutException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from typing import Optional

from my_series import *


class DownloadLinkDoesNotExist(Exception):
    pass


class DidNotFindDownloadLink(Exception):
    pass


class GetDownloadLink:
    def __init__(self):
        options = Options()
        options.add_argument("--headless=new")
        logging.getLogger("seleniumwire").setLevel(logging.WARNING)
        options.add_argument("--ignore-certificate-errors")

        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=options
        )
        print("Started webdriver.")

    def _kill_old_webdrivers(self) -> None:
        if sys.platform.startswith("win"):
            subprocess.call(
                "taskkill /F /IM chromedriver.exe /T",
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            subprocess.call(
                "taskkill /F /IM chrome.exe /T",
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

    def _wait_for_download_url(self) -> seleniumwire.request.Request:
        return self.driver.wait_for_request(
            ".m3u8|index-v1.m3u8|index-v1-a1.m3u8|(?=.*lightningbolts)(?=.*m3u8)",
            timeout=15,
        )

    @staticmethod
    def _site_name(url):
        return url.split("//")[1].split(".")[0]

    def _get_download_link_unknown(self, url):
        raise DownloadLinkDoesNotExist(f"The site - {url} is unknown")

    def get_subtitles_link(self, url) -> Optional[str]:
        # For example, calls "__get_url_123series(url), if none exists for site returns none."
        return getattr(
            self, f"_get_subtitles_{self._site_name(url)}", lambda url: None
        )(url)

    def get_download_link(self, url) -> seleniumwire.request.Request:
        del self.driver.requests  # clean old requests.
        return getattr(
            self,
            f"_get_download_link_{self._site_name(url)}",
            self._get_download_link_unknown,
        )(url)

    """
    These function names are important, it is called with getattr(self, "<func_name>_<site_name>").
    To add support for another site (new_site), one needs to implement _get_download_link_new_site, 
        if there are subtitles also _get_subtitles_new_site.
    """

    def _get_download_link_9animetv(self, url) -> seleniumwire.request.Request:
        print("Getting link from 9animetv")
        self.driver.get(url)
        return self.driver.wait_for_request(
            "index-f2-v1-a1.m3u8",
            timeout=15,
        )

    def _get_subtitles_9animetv(self, url) -> Optional[str]:
        self.driver.get(url)
        return self.driver.wait_for_request(
            "eng.*\\.vtt",
            timeout=15,
        ).url

    def _get_download_link_gomovie123(self, url) -> seleniumwire.request.Request:
        print("Getting link from gomovie123")
        self.driver.get(url)
        time.sleep(5)
        self.driver.find_elements(By.ID, "cover")[0].click()
        return self._wait_for_download_url()

    def __get_url_123series(self, url) -> None:
        self.driver.get(url)
        if not self.driver.find_elements(By.ID, "main-wrapper"):
            raise DownloadLinkDoesNotExist(f"{url} has no presentation of video :/")

    def _get_subtitles_123series(self, url) -> Optional[str]:
        self.__get_url_123series(url)
        time.sleep(5)  # need the subtitles to load properly...
        subtitles_dropdown = self.driver.find_elements(By.ID, "subtitles-dropdown")[0]
        for subtitles in subtitles_dropdown.children():  # type: ignore
            if SUBTITLE_LANGUAGE.lower() in subtitles.text.lower():
                print(f"found subtitles link in {url}")
                return subtitles.get_property("value")

    def __try_all_servers_123series(self, url) -> seleniumwire.request.Request:
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
                except selenium.common.exceptions.Ele + mentClickInterceptedException:  # type: ignore
                    print(f"Got an extremely annoying add, reloading the page")
                    self.driver.get(url)
                    break
                try:
                    return self._wait_for_download_url()
                except TimeoutException:
                    continue
        # It does not exist on all the servers
        raise DidNotFindDownloadLink(f"all the servers for {url} does not work :/")

    def _get_download_link_123series(self, url) -> seleniumwire.request.Request:
        self.__get_url_123series(url)
        try:
            return self._wait_for_download_url()
        except TimeoutException:
            print(f"Error downloading: {url}, Checing if other server works :/")
            return self.__try_all_servers_123series(url)
