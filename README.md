## GeoRetriever 🗿🐕
##### A Python package for array-based retrieval of geological data. In a second step, the data can be converted to localized thermal energy system suitability.

Based on the tools used in the great [atlite](https://github.com/PyPSA/atlite) package, GeoRetriever is supported by [dask](https://github.com/dask/dask) and [xarray](https://github.com/pydata/xarray) for parallelized requests of data chunks.
The thermal systems of most interest are

- Borehole Thermal Energy Storage (BTES)
- Aquifer Thermal Energy Storage (ATES)
- Shallow Ground Source Heat Pumps (CSHP)
- Pit Thermal Energy Storage (PTES)
- Mine Thermal Energy Storage (MTES)

The library is under development with more features being added in the future. This is a promise - I need this for my PhD 🧗🏼.

| Feature | Data Source | Coverage | Implemented |
|---------|-------------|----------|-------------|
| Lithology | [Macrostrat](https://macrostrat.org/)| global | ✔️|
| Surface Temperature | [ERA5](https://www.ecmwf.int/en/forecasts/datasets/reanalysis-datasets/era5) | global | ✔️ |
| Soil Temperature | [ERA5](https://www.ecmwf.int/en/forecasts/datasets/reanalysis-datasets/era5) | global | ✔️ |






