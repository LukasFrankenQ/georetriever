import os
import warnings
import numpy as np
import xarray as xr
import pandas as pd
from tempfile import mkstemp
import weakref
import cdsapi
import logging
from numpy import atleast_1d

from gis import maybe_swap_spatial_dims

try:
    from contextlib import nullcontext
except ImportError:
    import contextlib

    @contextlib.contextmanager
    def nullcontext():
        yield


logger = logging.getLogger(__name__)

crs = 4326

logging.warn("Era 5 missing features: height")
features = {"temperature": ["temperature", "soil temperature"]}

static_features = {"height"}


def _rename_and_clean_coords(ds, add_lon_lat=True):
    """Rename 'longitude' and 'latitude' columns to 'x' and 'y' and fix roundings.
    Optionally (add_lon_lat, default:True) preserves latitude and longitude
    columns as 'lat' and 'lon'.
    """
    ds = ds.rename({"longitude": "x", "latitude": "y"})
    # round coords since cds coords are float32 which would lead to mismatches
    ds = ds.assign_coords(
        x=np.round(ds.x.astype(float), 5), y=np.round(ds.y.astype(float), 5)
    )
    ds = maybe_swap_spatial_dims(ds)
    if add_lon_lat:
        ds = ds.assign_coords(lon=ds.coords["x"], lat=ds.coords["y"])
    return ds


def get_data_temperature(retrieval_params):
    """Get wind temperature for given retrieval parameters."""
    ds = retrieve_data(
        variable=["2m_temperature", "soil_temperature_level_4"], **retrieval_params
    )

    ds = _rename_and_clean_coords(ds)
    ds = ds.rename({"t2m": "temperature", "stl4": "soil temperature"})

    return ds


def _area(coords):
    # North, West, South, East. Default: global
    x0, x1 = coords["x"].min().item(), coords["x"].max().item()
    y0, y1 = coords["y"].min().item(), coords["y"].max().item()
    return [y1, x0, y0, x1]


def retrieval_times(coords, static=False):
    """
    Get list of retrieval cdsapi arguments for time dimension in coordinates.
    If static is False, this function creates a query for each year in the
    time axis in coords. This ensures not running into query limits of the
    cdsapi. If static is True, the function return only one set of parameters
    for the very first time point.
    Parameters
    ----------
    coords : atlite.Cutout.coords
    Returns
    -------
    list of dicts witht retrieval arguments
    """
    time = coords["time"].to_index()
    if static:
        return {
            "year": str(time[0].year),
            "month": str(time[0].month),
            "day": str(time[0].day),
            "time": time[0].strftime("%H:00"),
        }

    times = []
    for year in time.year.unique():
        t = time[time.year == year]
        query = {
            "year": str(year),
            "month": list(t.month.unique()),
            "day": list(t.day.unique()),
            "time": ["%02d:00" % h for h in t.hour.unique()],
        }
        times.append(query)
    return times


def noisy_unlink(path):
    """Delete file at given path."""
    logger.debug(f"Deleting file {path}")
    try:
        os.unlink(path)
    except PermissionError:
        logger.error(f"Unable to delete file {path}, as it is still in use.")


def retrieve_data(product, chunks=None, tmpdir=None, lock=None, **updates):
    """
    Download data like ERA5 from the Climate Data Store (CDS).
    If you want to track the state of your request go to
    https://cds.climate.copernicus.eu/cdsapp#!/yourrequests
    """

    request = {"product_type": "reanalysis", "format": "netcdf"}
    request.update(updates)

    assert {"year", "month", "variable"}.issubset(
        request
    ), "Need to specify at least 'variable', 'year' and 'month'"

    client = cdsapi.Client(
        info_callback=logger.debug, debug=logging.DEBUG >= logging.root.level
    )
    result = client.retrieve(product, request)

    if lock is None:
        lock = nullcontext()

    with lock:
        fd, target = mkstemp(suffix=".nc", dir=tmpdir)
        os.close(fd)

        yearstr = ", ".join(atleast_1d(request["year"]))
        variables = atleast_1d(request["variable"])
        varstr = "".join(["\t * " + v + f" ({yearstr})\n" for v in variables])
        logger.info(f"CDS: Downloading variables\n{varstr}")
        result.download(target)

    ds = xr.open_dataset(target, chunks=chunks or {})
    # if tmpdir is None:
    # logger.debug(f"Adding finalizer for {target}")
    # weakref.finalize(ds._file_obj._manager, noisy_unlink, target)

    return ds


def get_data(geocutout, feature, tmpdir=None, lock=None, **creation_parameters):

    coords = geocutout.coords

    retrieval_params = {
        "product": "reanalysis-era5-single-levels",
        "area": _area(geocutout.coords),
        "chunks": geocutout.chunks,
        "grid": [geocutout.dx, geocutout.dy],
        "lock": lock,
    }

    coords = geocutout.coords

    func = globals().get(f"get_data_{feature}")

    def retrieve_once(time):
        return func({**retrieval_params, **time})

    datasets = map(retrieve_once, retrieval_times(coords))

    return xr.concat(datasets, dim="time").sel(time=coords["time"])
