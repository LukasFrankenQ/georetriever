## GeoRetriever 🌋🐕

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)


##### A Python package for array-based retrieval of geological data. In a second step (available in a future version), the data can be converted to localized thermal energy system suitability.

Based on the tools used in the great [atlite](https://github.com/PyPSA/atlite) package, GeoRetriever is supported by [dask](https://github.com/dask/dask) and [xarray](https://github.com/pydata/xarray) for parallelized requests of data chunks.
When completed, the package will be able to retrieve all data relevant the following thermal systems:

- Borehole Thermal Energy Storage (BTES)
- Aquifer Thermal Energy Storage (ATES)
- Shallow Ground Source Heat Pumps (CSHP)
- Water Source Heat Pumps (WSHP)
- Pit Thermal Energy Storage (PTES)
- Mine Thermal Energy Storage (MTES)

The library is under development with more features being added in the future. This is a promise - I need this for my PhD 🧗🏼.

| Feature | Data Source | Coverage | Implemented |
|---------|-------------|----------|-------------|
| Lithology | [Macrostrat](https://macrostrat.org/)| global | ✔️|
| Surface Temperature | [ERA5](https://www.ecmwf.int/en/forecasts/datasets/reanalysis-datasets/era5) | global | ✔️ |
| Soil Temperature | [ERA5](https://www.ecmwf.int/en/forecasts/datasets/reanalysis-datasets/era5) | global | ✔️ |
| Aquifer Presence |  | | ❌ |
| Soil Type |  | | ❌ |

### Installation

The package runs on `Python>=3.6` and is available from `pypi` via
```
pip install georetriever
```

Note that for the feauture `"temperature"`, the API to `ERA5` will be used, which requires registration and setting up of the CDS API key as [here](https://cds.climate.copernicus.eu/api-how-to).

### Example

The package works through the `GeoCutout` object. During its initialization, the  spatial and temporal scale of the data is defined. Coordinates are in `(lon, lat)`. The actual retrieval of data starts when the `prepare()`, which takes the features of interest are passed method is called.
For instance:
```
from georetriever import GeoCutout

x = slice(-1, 1)
y = slice(50, 52)
dx = 0.05
dy = 0.05
time = "2019-01-01"
dt = "h"

geocutout = GeoCutout(
    x=x,
    y=y,
    dx=dx,
    dy=dy,
    time=time,
    dt=dt,
)

geocutout.prepare(features=["temperature", "lithology"])

print(geocutout.data)
```

### Authors and Contact

__Lukas Franken__ - [lukas.franken@ed.ac.uk](lukas.franken@ed.ac.uk)
University of Edinburgh, Alan Turing Institute

Big thanks to the team an __TU Berlin__ for [atlite](https://github.com/pypsa/atlite), the package this library is leaning on.