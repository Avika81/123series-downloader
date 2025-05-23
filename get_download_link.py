import time
import selenium
import seleniumwire.undetected_chromedriver as webdriver

# replace with above if undetected is not your thing
# from seleniumwire import webdriver
from seleniumwire.inspect import TimeoutException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

from my_series import *


class DownloadLinkDoesNotExist(Exception):
    pass


class DidNotFindDownloadLink(Exception):
    pass


class GetDownloadLink:
    def __init__(self):
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--ignore-certificate-errors")

        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=options
        )
        print("Started webdriver.")

    def _wait_for_download_url(self):
        return self.driver.wait_for_request(
            ".m3u8|index-v1.m3u8|index-v1-a1.m3u8|(?=.*lightningbolts)(?=.*m3u8)",
            timeout=15,
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

    def get_subtitles_link(self, url):
        if url.startswith("https://gomovie123"):
            return
        self._get_url(url)
        time.sleep(5)  # need the subtitles to load properly...
        subtitles_dropdown = self.driver.find_elements(By.ID, "subtitles-dropdown")[0]
        for subtitles in subtitles_dropdown.children():
            if SUBTITLE_LANGUAGE.lower() in subtitles.text.lower():
                print(f"found subtitles link in {url}")
                return subtitles.get_property("value")

    def _get_url(self, url):
        self.driver.get(url)
        if not self.driver.find_elements(By.ID, "main-wrapper"):
            raise DownloadLinkDoesNotExist(f"{url} has no presentation of video :/")

    def _get_link_gomovie123(self, url):
        print("Getting link from gomovie123")
        self.driver.get(url)
        time.sleep(5)
        self.driver.find_elements(By.ID, "cover")[0].click()
        return self._wait_for_download_url()

    def get_download_link(self, url):
        del self.driver.requests  # clean old requests.
        if url.startswith("https://gomovie123"):
            return self._get_link_gomovie123(url)
        self._get_url(url)
        try:
            return self._wait_for_download_url()
        except TimeoutException:
            print(f"Error downloading: {url}, Checing if other server works :/")
            return self._try_all_servers(url)
