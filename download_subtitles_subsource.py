from pathlib import Path
import requests
from download_movies import MOVIES_PATH
from subsource_account import API_KEY
import zipfile
import io

# https://subsource.net/api-docs


def __request(api, params={}):
    BASE_URL = "https://api.subsource.net/api/v1"
    return requests.get(
        f"{BASE_URL}/{api}",
        params=params,
        headers={"X-API-KEY": API_KEY, "Content-Type": "application/json"},
    )


def _request(api, params={}) -> dict:
    response = __request(api, params=params).json()
    if not response["success"]:
        print("Got error from subsource.net, debugging...")
        import IPython

        IPython.embed()

    return response["data"]


def get_subtitles_content(subtitle_id) -> bytes:
    download_response = __request("subtitles/{id}/download".format(id=subtitle_id))
    if download_response.ok:
        zf = zipfile.ZipFile(io.BytesIO(download_response.content))
        for f in zf.namelist():
            return zf.open(f).read()
    raise RuntimeError("Could not download file.")


def download_subtitles(movie_id: int) -> bytes:
    subtitles_list = _request(
        api="subtitles", params={"movieId": movie_id, "language": "english"}
    )

    for subtitle in subtitles_list:
        try:
            return get_subtitles_content(subtitle["subtitleId"])
        except RuntimeError:
            pass
    raise RuntimeError(f"Did not find a matching subtitles for id {movie_id}")


def search_movie(name: str, season=1) -> int:
    response = _request(
        api="movies/search", params={"searchType": "text", "q": name, "season": season}
    )

    for movie in response:
        if (
            movie["title"].lower().replace(":", "") == name.lower()
            and movie["subtitleCount"] > 0
        ):
            return movie["movieId"]

    raise RuntimeError(
        "Did not find a matching movie, take a look over these names if one fits: {}".format(
            [m["title"] for m in response]
        )
    )


def download_subtitles_for_movie(path):
    if path.suffix == ".mp4":
        subtitles_file = Path(str(path).replace(".mp4", ".vtt"))
        if not subtitles_file.is_file():
            print("Finding subtitles for {}".format(path.name.strip(".mp4")))
            movie_id = search_movie(path.name.replace(".mp4", "").replace("-", " "))
            subtitles = download_subtitles(movie_id)
            with open(subtitles_file, "wb") as of:
                of.write(subtitles)


def download_episode(season, episode, subtitles_file, subtitles_list):
    for s in subtitles_list:
        release_name = s["releaseInfo"][0].lower()
        if (
            f"s{season:02}e{episode:02}" in release_name
            or f"chapter {int(episode)}" in release_name
        ):
            subtitles = get_subtitles_content(s["subtitleId"])
            with open(subtitles_file, "wb") as of:
                of.write(subtitles)
                return

    raise RuntimeError(f"Could not download for episode: {season} - {episode}")


def download_subtitles_for_season(serie_name, season):
    movie_id = search_movie(
        serie_name.replace(".mp4", "").replace("-", " "), season=season
    )
    subtitles_list = _request(
        api="subtitles",
        params={"movieId": movie_id, "language": "english", "limit": 100},
    )
    for f in (Path(__file__).parent / "series" / serie_name / f"{season:02}").iterdir():
        if f.suffix == ".mp4":
            # the names are season-episode.something
            episode = f.name.split("-")[1].split(".")[0]
            subtitles_file = Path(str(f).replace(".mp4", ".vtt"))
            if not subtitles_file.exists():
                try:
                    download_episode(
                        season=season,
                        episode=episode,
                        subtitles_file=subtitles_file,
                        subtitles_list=subtitles_list,
                    )
                except RuntimeError as e:
                    print(e)


if __name__ == "__main__":
    # download for all movies:
    for f in MOVIES_PATH.iterdir():
        download_subtitles_for_movie(f)

    # download for a serie:
    for season in range(1, 20):
        download_subtitles_for_season("family guy", season=season)
