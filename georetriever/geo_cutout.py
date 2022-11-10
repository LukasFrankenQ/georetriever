import os
import xarray as xr
import pandas as pd
import numpy as np
import dask
import geopandas as gpd
import rasterio as rio

from shapely.geometry import box
from pathlib import Path
from pyproj import CRS

from .gis import get_coords
from .utils import Lith
from .data import geocutout_prepare

import logging

logger = logging.getLogger(__name__)


class GeoCutout:

    CRS = 4326

    def __init__(self, path, **cutoutparams):
        """
        Adapted from 'Cutout' in the amazing "atlite" package

        Provides frame and grid to obtain and store GeoRetriever data

        Checks if the cutout already exists, and loads it if so.
        O/w prepares the data to fill the cutout

        Parameters
        ----------
        path : str | path-like
            NetCDF from which to load or where to store the cutout
        x : slice, optional
            Outer longitudinal bounds for the cutout (west, east)
        y : slice, optional
            Outer latitudinal bounds for the cutout (south, north)
        time : str | slice
            Time range to include in the cutout, e.g. "2011" or
            ("2011-01-05", "2011-01-25")
            This is necessary when building a new cutout.
        dx : float, optional
            Step size of the x coordinate. The default is 0.25
        dy : float, optional
            Step size of the y coordinate. The default is 0.25
        dt : str, optional
            Frequency of the time coordinate. The default is 'h'. Valid are all
            pandas offset aliases.
        """

        self._prepared = False

        path = Path(path).with_suffix(".nc")

        logger.debug("To be implemented: method to load path and check existence")
        if False:
            # Implement cutout-loading here
            pass
        else:
            logger.info(f"Building new cutout {path}")

            try:
                x = cutoutparams.pop("x")
                y = cutoutparams.pop("y")
                time = cutoutparams.pop("time")
            except KeyError as exc:
                raise TypeError(
                    "Arguments 'time' and 'module' must be "
                    "specified. Spatial bounds must either be "
                    "passed via argument 'bounds' or 'x' and 'y'."
                ) from exc

            coords = get_coords(x, y, time, **cutoutparams)

            attrs = {"prepared_features": list(), **cutoutparams}

            data = xr.Dataset(coords=coords, attrs=attrs)

        self.data = data
        self.path = path

    def prepare(self, *args, **kwargs):
        """Obtains the data. See data.geocutout_prepare for details"""
        geocutout_prepare(self, *args, **kwargs)

    def to_netcdf(self, filename):
        """
        Wrapper of xarray.Dataset().to_netcdf that makes parts of retrieved data
        storable before storing
        """
        self.to_saveable_mode()
        self.data.to_netcdf(filename)
        self.to_object_mode()

    @staticmethod
    def open_dataset(filename):
        """
        Wrapper of xarray.open_dataset() that reads filename and transforms
        retrieved data into object mode.
        Overwrites self.data
        """
        ds = xr.open_dataset(filename)
        if "major" in ds.variables:
            ds["lithology"] = Lith.to_dataarray(ds)
        ds = ds.drop(Lith.index)
        return ds

    def to_saveable_mode(self):
        """
        Sends self.data to saveable_mode, where some functionalities
        are not available but self.data can be saved as netcdf
        """
        if self._saveable_mode:
            return
        self.data = xr.merge([self.data, Lith.to_dataset(self.data["lithology"])])
        self.data = self.data.drop("lithology")

    def to_object_mode(self):
        """
        Sends self.data to object_mode, where some functionalities are
        available but self.data can not be saved as netcdf
        """
        if self._object_mode:
            return
        self.data["lithology"] = Lith.to_dataarray(self.data)
        self.data = self.data.drop(Lith.index)

    @property
    def _object_mode(self):
        """If True, self.data contains custom objects such as utils.Lith,
        can not be stored as a netcdf in that case, but has additional
        functionality"""
        try:
            self.data.to_netcdf("hold.nc")
            os.remove("hold.nc")
        except ValueError:
            return True

        return False

    @property
    def _saveable_mode(self):
        """Returns if self.data can currently be stored as a netcdf"""
        return not self._object_mode

    @property
    def name(self):
        """name of the cutout"""
        return self.path

    @property
    def crs(self):
        """Coordinate reference system of cutout"""
        return self.CRS

    @property
    def available_features(self):
        """Lists available geodata for the cutout"""
        raise NotImplementedError("implement me")

    @property
    def coords(self):
        """Geographic coordinate of the cutout"""
        return self.data.coords

    @property
    def dx(self):
        """Spatial resolution on the x coordinates."""
        x = self.coords["x"]
        return round((x[-1] - x[0]).item() / (x.size - 1), 8)

    @property
    def dy(self):
        """Spatial resolution on the y coordinates."""
        y = self.coords["y"]
        return round((y[-1] - y[0]).item() / (y.size - 1), 8)

    @property
    def extent(self):
        """Total extent of the area covered by the cutout (x, X, y, Y)"""
        xs, ys = self.coords["x"].values, self.coords["y"].values
        dx, dy = self.dx, self.dy
        return np.array(
            [xs[0] - dx / 2, xs[-1] + dx / 2, ys[0] - dy / 2, ys[-1] + dy / 2]
        )

    @property
    def bounds(self):
        """Total bounds of the area covered by the cutout (x, y, X, Y)."""
        return self.extent[[0, 2, 1, 3]]

    @property
    def prepared(self):
        """Boolean indicating if all features have been prepared"""
        logging.warning("GeoCutout.prepared is not yet fully implemented")
        return self._prepared

    @property
    def chunks(self):
        """Chunking of the cutout data used by dask."""
        chunks = {
            k.lstrip("chunksize_"): v
            for k, v in self.data.attrs.items()
            if k.startswith("chunksize_")
        }
        return None if chunks == {} else chunks
