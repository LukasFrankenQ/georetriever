import pandas as pd
import xarray as xr
import os
from numpy import atleast_1d
from tempfile import mkstemp, mkdtemp
from shutil import rmtree
from functools import wraps
from dask import delayed, compute
from dask.utils import SerializableLock
from dask.diagnostics import ProgressBar

import logging
logger = logging.getLogger(__name__)

from datasets import modules as datamodules
from utils.geo_utils import Lith

feature_mapping = {
    "temperature": "era5",
    "lithology": "macrostrat",
}


def get_feature(geocutout, module, feature, tmpdir=None):
    """
    Load the feature data for a given module.
    This get the data for a set of features from a module. All modules in
    `atlite.datasets` are allowed.
    """

    parameters = geocutout.data.attrs
    lock = SerializableLock()
    datasets = list()

    get_data = datamodules[module].get_data
     
    feature_data = delayed(get_data)(
        geocutout, feature, tmpdir=tmpdir, lock=lock, **parameters
    )
    datasets.append(feature_data)

    datasets = compute(*datasets)

    ds = xr.merge(datasets, compat="equals")

    for v in ds:
        
        ds[v].attrs["module"] = module
        fd = datamodules[module].features.items()
        ds[v].attrs["features"] = [k for k, l in fd if v in l].pop()

    return ds


def maybe_remove_tmpdir(func):
    "Use this wrapper to make tempfile deletion compatible with windows machines."

    @wraps(func)
    def wrapper(*args, **kwargs):
        if kwargs.get("tmpdir", None):
            res = func(*args, **kwargs)
        else:
            kwargs["tmpdir"] = mkdtemp()
            try:
                res = func(*args, **kwargs)
            finally:
                rmtree(kwargs["tmpdir"])
        return res

    return wrapper    

def non_bool_dict(d):
    """Convert bool to int for netCDF4 storing"""
    return {k: v if not isinstance(v, bool) else int(v) for k, v in d.items()}


def make_storable(ds):
    """
    Ensures xr.Dataset can be stored as netcdf 
    This entails:
        - transforming xr.DataArray of Lith objects into a xr.Dataset of str

    Args:
        ds(xr.Dataset): dataset to be made convertible into netcdf
    
    Returns:
        xr.Dataset
    """ 
    
    if "lithology" in ds.variables:
        lith = ds["lithology"]
        ds = ds.drop("lithology")
        ds = xr.merge([ds, Lith.to_dataset(lith)]) 

    return ds


@maybe_remove_tmpdir
def geocutout_prepare(geocutout, 
                      features=None, 
                      tmpdir=None, 
                      overwrite=False):

    """
    Parameters
    ----------
    cutout : geo_retriever.GeoCutout
    features : str/list, optional
        Feature(s) to be prepared. The default slice(None) results in all
        available features.
    tmpdir : str/Path, optional
        Directory in which temporary files (for example retrieved ERA5 netcdf
        files) are stored. If set, the directory will not be deleted and the
        intermediate files can be examined.
    overwrite : bool, optional
        Whether to overwrite variables which are already included in the
        cutout. The default is False.
    Returns
    -------
    geocutout : geo_retriever.GeoCutout
        GeoCutout with prepared data. The variables are stored in `geocutout.data`.
    """

    logger.warning("Overwrite not yet implemented")

    if geocutout.prepared and not overwrite:
        logger.info("GeoCutout already prepared") 
        return geocutout
    
    logger.info(f"Storing temporary files in {tmpdir}")
   
    features = atleast_1d(features) if features else slice(None)
    prepared = list(atleast_1d(geocutout.data.attrs["prepared_features"]))

    logging.warning("Double download of prepared features not yet prevented")

    for feature in features:
        assert feature in feature_mapping, f"No module for feature {feature} " + \
            f"\n Available features: {feature_mapping}"

    logging.warning("Double importing not prevented yet")
    for feature in features:
        module = feature_mapping[feature]

        logging.info(f"Calculating {feature} with module {module}:") 

        ds = get_feature(geocutout, module, feature, tmpdir=tmpdir)

        prepared += [key for key in ds.keys()]

        geocutout.data.attrs.update(dict(
            prepared_features=list(prepared)
            ))

        attrs = non_bool_dict(geocutout.data.attrs)
        attrs.update(ds.attrs)

        ds = geocutout.data.merge(ds).assign_attrs(**attrs)

        directory, filename = os.path.split(str(geocutout.path))
        fd, tmp = mkstemp(suffix=filename, dir=directory)

        os.close(fd)


        with ProgressBar():
            print(ds)
            make_storable(ds).to_netcdf(tmp)
        
        if geocutout.path.exists():
            geocutout.data.close()
            geocutout.path.unlink()
        os.rename(tmp, geocutout.path)

        geocutout.data = xr.open_dataset(geocutout.path, chunks=geocutout.chunks) 

    geocutout.to_object_mode()

    return geocutout 