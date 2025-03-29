import json
from pathlib import Path
from seleniumwire.request import Request


def get_links_file_path(serie_name):
    path = Path(__file__).parent / "links" / f"{serie_name}.json"
    if not path.is_file():
        with open(path, "w") as f:
            json.dump({}, f, indent=4)
    return path


def read_links(serie_name):
    with open(get_links_file_path(serie_name)) as f:
        return {
            name: Request(
                url=req_data["url"],
                method=req_data["method"],
                headers=req_data["headers"],
            )
            for name, req_data in json.load(f)
        }


def add_video(serie_name, name, req):
    with open(get_links_file_path(serie_name)) as f:
        to_download = json.load(f)

    to_download[name] = {
        "url": req.url,
        "method": req.method,
        "headers": dict(req.headers),
    }
    with open(get_links_file_path(serie_name), "w") as f:
        json.dump(to_download, f, indent=4)
