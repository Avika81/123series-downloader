# Downloads series automatically from 123series.art

## How to download a new serie?

- `my_series.py`: add a serie/movie URL URL, for example:
  - ```python
    SERIES = [serie_from_url(url) fpr url in ["https://123series.art/series/<SERIE>"]
    ```
- run `python download_series.py` or `python download_movies.py`.

## requirements:

- `pip install -r requirements.txt`
- `python -m seleniumwire extractcert`
- `certutil -addstore -f "Root" ca.crt`
