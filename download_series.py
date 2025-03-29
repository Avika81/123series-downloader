from pathlib import Path
from downloader import DownloadVideos
from get_download_link import DownloadLinkDoesNotExist, GetDownloadLink
from my_series import *
from serie import Serie

URL_TEMPLATE = "https://123series.art/series/{name}/{season}-{episode}/"
MAX_EPISODE = 400  # more than this and you should not watch this serie


def get_filename(serie, season, episode):
    return (
        Path(__file__).parent
        / "series"
        / serie.human_name
        / f"{season:02}-{episode:02}.mp4"
    )


def add_episode(
    serie: Serie, season: int, gvl: GetDownloadLink, episode: int, to_download: dict
):
    to_download[get_filename(serie=serie, season=season, episode=episode)] = (
        gvl.get_download_link(
            URL_TEMPLATE.format(name=serie.name, season=season, episode=episode)
        )
    )


def get_season_links(
    serie: Serie, season: int, gvl: GetDownloadLink, to_download: dict
):
    for episode in range(1, MAX_EPISODE):
        try:
            add_episode(
                serie=serie,
                season=season,
                gvl=gvl,
                episode=episode,
                to_download=to_download,
            )
        except DownloadLinkDoesNotExist:
            break
        except Exception as e:
            # Problem with specific episode, log and try the next one :)
            print(
                f"Error - {repr(e)}, trying to download {serie.human_name}:{season}-{episode}"
            )
            continue


def main():
    # TODO: clean this code
    gvl = GetDownloadLink()
    to_download = {}
    for serie in SERIES:
        for season in range(1, 20):
            for episode in range(1, MAX_EPISODE):
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
    gvl.driver.quit()
    DownloadVideos(to_download=to_download).start_downloads()


if __name__ == "__main__":
    main()
