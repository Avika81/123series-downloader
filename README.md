# Downloads series automatically from 123series.art

## How to download a new serie?

- `my_series.py`: add a serie/movie URL URL, for example:
  - ```python
    from serie import serie_from_url

    SUBTITLE_LANGUAGE = "English"
    SERIES = [serie_from_url(url) for url in ["https://123series.art/series/<SERIE>"]
    MOVIES = ["https://123series.art/movie/<MOVIE>"]
    ```
- run `python download_series.py` or `python download_movies.py`.

## requirements:

- `pip install -r requirements.txt`
- `Install ffmpeg` 
