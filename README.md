# Downloads series automatically from 123series.art

## How to download a new serie?

- `series.py`: add a serie you want to download (name+URL in 123series.art name).
- `get_download_links.py`: choose the seasons you want to download, and get the links file (will create a json with download links in `links/serie_name`)
- `download_videos.py`: runs ffmpeg download for all the links in the given folder, downloads to the `series/` directory.

## requirements:

- pip install -r requirements.txt
