import xarray as xr
import pandas as pd
import numpy as np
import dask
import geopandas as gpd
import rasterio as rio

from shapely.geometry import box
from pathlib import Path
from pyproj import CRS

from gis import get_coords

import logging

logger = logging.getLogger(__name__)

class GeoCutout:
    
    CRS = "EPSG:4236"
    
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
        dx : float, optional
            Step size of the x coordinate. The default is 0.25
        dy : float, optional
            Step size of the y coordinate. The default is 0.25
        """
        
        path = Path(path).with_suffix('.nc')

        logger.debug('To be implemented: method to load path and check existence') 
        if False:
            # Implement cutout-loading here
            pass 
        else:
            logger.info(f"Building new cutout {path}") 
           
            try:
                x = cutoutparams.pop('x') 
                y = cutoutparams.pop('y') 
            except KeyError:
                raise TypeError("x, y must be provided as slice")   
                
            coords = get_coords(x, y)

            attrs = {
                "prepared_features": list(),
                **cutoutparams
            }

            data = xr.Dataset(coords=coords, attrs=attrs)
            
        self.data = data
        self.path = path

    
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

        

