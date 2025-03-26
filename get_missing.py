from pathlib import Path
from download_videos import DownloadVideos
from get_download_links import (
    EpisodeDoesNotExist,
    GetVideoLinks,
    add_episode,
)
from series import THE_BLACKLIST


def get_missing(serie):
    dv = DownloadVideos(serie.human_name)
    gvl = GetVideoLinks()
    for season in range(1, 10):
        for episode in range(1, 30):
            if not Path(dv.get_filename(f"{season:02}-{episode:02}")).exists():
                print(f"f{season}:{episode} is missing, getting its link")
                try:
                    add_episode(serie=serie, gvl=gvl, episode=episode, season=season)
                except EpisodeDoesNotExist:
                    break
                except Exception:
                    print(f"did not found a link for {season}:{episode} :(")
                    continue
    dv.start_downloads()


if __name__ == "__main__":
    get_missing(THE_BLACKLIST)
