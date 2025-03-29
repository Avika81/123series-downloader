from download_videos import DownloadVideos
from get_download_links import (
    URL_TEMPLATE,
    EpisodeDoesNotExist,
    GetVideoLinks,
    get_filename,
)
from series import THE_BLACKLIST


def get_missing(serie):
    gvl = GetVideoLinks()
    to_download = {}
    for season in range(1, 10):
        for episode in range(1, 30):
            name = get_filename(serie=serie, season=season, episode=episode)
            if not name.exists():
                print(f"f{season}:{episode} is missing, getting its link")
                try:
                    to_download[name] = gvl.get_download_link(
                        URL_TEMPLATE.format(
                            name=serie.name, season=season, episode=episode
                        )
                    )
                except EpisodeDoesNotExist:
                    break
                except Exception:
                    print(f"did not found a link for {season}:{episode} :(")
                    continue
    DownloadVideos(to_download).start_downloads()


if __name__ == "__main__":
    get_missing(THE_BLACKLIST)
