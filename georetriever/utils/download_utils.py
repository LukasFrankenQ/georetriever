import wget
import os
import urllib.request
from wsl_pathlib.path import WslPath as Path
from zipfile import ZipFile


def maybe_download(filepath, url):
    """
    Checks if file exists.
    If not downloads url, stores it as filepath

    Args:
        filepath(str): path to file (or where it will be stored)
        url(str): download link

    """

    assert (
        "watershed" not in url
    ), "Use maybe_download_watershed() to download watershed data"

    if not os.path.exists(filepath):
        filepath = Path(filepath)

        os.makedirs(filepath.parent, exist_ok=True)
        wget.download(url, out=filepath)


def maybe_download_watershed(datapath, url):
    """
    Checks if file exists.

    if not downloads it. Watershed download origin requires
    specific header and hence warrants a separate function

    Args:
        datapath(str): path to dir (or where it will be stored)
        url(str): download link
    """

    if os.path.exists(datapath) and len(os.listdir(datapath)) > 0:
        return

    datapath = Path(datapath)

    datapath.parent.mkdir(parents=True, exist_ok=True)

    opener = urllib.request.URLopener()
    opener.addheader(
        "User-Agent",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36",
    )

    zip_path = Path(str(datapath) + ".zip")

    opener.retrieve(url, zip_path)

    with ZipFile(zip_path, "r") as zip:
        zip.extractall(path=datapath)


if __name__ == "__main__":
    pass
