from downloader import DownloadVideos
from get_download_link import (
    URL_TEMPLATE,
    DownloadLinkDoesNotExist,
    GetDownloadLink,
    get_filename,
)
from my_series import THE_BLACKLIST


def get_missing(serie):
    gvl = GetDownloadLink()
    to_download = {}
    for season in range(1, 10):
        for episode in range(1, 30):
            name = get_filename(serie=serie, season=season, episode=episode)
            if not name.exists():
                try:
                    to_download[name] = gvl.get_download_link(
                        URL_TEMPLATE.format(
                            name=serie.name, season=season, episode=episode
                        )
                    )
                    print(f"Added missing: f{season}:{episode}")
                except DownloadLinkDoesNotExist:
                    break
                except Exception:
                    print(f"did not found a link for {season}:{episode} :(")
                    continue
    DownloadVideos(to_download=to_download).start_downloads()


if __name__ == "__main__":
    get_missing(THE_BLACKLIST)
