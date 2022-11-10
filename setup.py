from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = "0.0.3"
DESCRIPTION = "Retrieve geological information from coordinates in Python!"
LONG_DESCRIPTION = "See description"

# Setting up
setup(
    name="geo_retriever",
    version=VERSION,
    author="Hui Ben, Lukas Franken, Heather Kennedy, Nikolaos Reppas",
    author_email="<lukas.franken@ed.ac.uk>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=["geopandas"],
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
