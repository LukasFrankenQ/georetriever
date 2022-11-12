from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = "0.1.0"
DESCRIPTION = (
    "Retrieve geological data for geothermal systems from coordinates in Python!"
)
LONG_DESCRIPTION = "See README.me at github.com/LukasFrankenQ/georetriever"

# Setting up
setup(
    name="georetriever",
    version=VERSION,
    author="Lukas Franken, Hui Ben, Heather Kennedy, Nikolaos Reppas",
    author_email="<lukas.franken@ed.ac.uk>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=[
        "numpy",
        "pandas>=0.25",
        "geopandas",
        "dask>=0.18.0 ,<2021.04.0",
        "xarray>=0.16.2",
        "Pillow",
        "rasterio>=1.2.10",
        "cdsapi",
        "netcdf4",
        "scipy",
        "toolz",
        "pyproj>=2.0",
        "shapely",
        "tqdm",
        "progressbar2",
    ],
    keywords=[
        "python",
        "geo",
        "geological",
        "heatflow",
        "thermal",
        "lithography",
        "conductivity",
    ],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ],
)
