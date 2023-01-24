import wget
import os
from pathlib import Path
import urllib.request


def maybe_download(filepath, url):
    """
    Checks if file exists.
    If not downloads url, stores it as filepath

    Args:
        filepath(str): path to file (or where it will be stored)
        url(str): download link

    """

    assert (
        "watershed" in url
    ), "Use maybe_download_watershed() to download watershed data"

    if not os.path.exists(filepath):
        filepath = Path(filepath)

        os.makedirs(filepath.parent, exist_ok=True)
        wget.download(url, out=filepath)


def maybe_download_watershed():

    opener = urllib.request.URLopener()
    opener.addheader(
        "User-Agent",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36",
    )


if __name__ == "__main__":
    maybe_download()
