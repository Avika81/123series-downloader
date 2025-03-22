import json
from pathlib import Path


def get_links_file_path(serie_name):
    path = Path(__file__).parent / "links" / f"{serie_name}.json"
    if not path.is_file():
        with open(path, "w") as f:
            json.dump({}, f, indent=4)
    return path
