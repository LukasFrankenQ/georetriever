"""
Adapted from atlite.gis
"""

import numpy as np
import pandas as pd
import xarray as xr
import scipy
import geopandas as gpd
import rasterio as rio

import logging

logger = logging.getLogger(__name__)


def get_coords(x, y, time, dx=0.25, dy=0.25, dt="h"):
    """
    Create GeoCutout coordinate system on the basis of slices and step sizes

    Parameters
    ----------
    x : slice
        Numerical slices with lower and upper bound of the x dimension.
    y : slice
        Numerical slices with lower and upper bound of the y dimension.
    dx : float, optional
        Step size of the x coordinate. The default is 0.25.
    dy : float, optional
        Step size of the y coordinate. The default is 0.25.

    Returns
    ----------
    ds : xarray.Dataset
        Dataset with x and y variables, representing the
        whole coordinate system.
    """

    x = slice(*sorted([x.start, x.stop]))
    y = slice(*sorted([y.start, y.stop]))

    ds = xr.Dataset(
        {
            "x": np.around(np.arange(-180, 180, dx), 9),
            "y": np.around(np.arange(-90, 90, dy), 9),
            "time": pd.date_range(start="1959", end="now", freq=dt),
        }
    )

    ds = ds.assign_coords(lon=ds.coords["x"], lat=ds.coords["y"])
    ds = ds.sel(x=x, y=y, time=time)

    return ds


def maybe_swap_spatial_dims(ds, namex="x", namey="y"):
    """Swap order of spatial dimensions according to atlite concention."""
    swaps = {}
    lx, rx = ds.indexes[namex][[0, -1]]
    ly, uy = ds.indexes[namey][[0, -1]]

    if lx > rx:
        swaps[namex] = slice(None, None, -1)
    if uy < ly:
        swaps[namey] = slice(None, None, -1)

    return ds.isel(**swaps) if swaps else ds
