'''
Adapted from atlite.gis
'''

import numpy as np
import pandas as pd
import xarray as xr
import scipy
import geopandas as gpd
import rasterio as rio

import logging

logger = logging.getLogger(__name__)


def get_coords(x, y, dx=0.25, dy=0.25):
    '''
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
    ''' 

    x = slice(*sorted([x.start, x.stop]))
    y = slice(*sorted([y.start, y.stop]))
    
    ds = xr.Dataset(
        {
            "x": np.around(np.arange(-180, 180, dx), 9),
            "y": np.around(np.arange(-90, 90, dy), 9),
        }
    )

    ds = ds.assign_coords(lon=ds.coords["x"], lat=ds.coords["y"])
    ds = ds.sel(x=x, y=y)

    return ds
    