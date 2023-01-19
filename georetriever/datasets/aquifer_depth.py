import xarray as xr
import pandas as pd
import os
import numpy as np
from scipy.interpolate import griddata

# aquifer_link = "https://agupubs.onlinelibrary.wiley.com/action/downloadSupplement?doi=10.1029%2F2007GL032244&file=grl24037-sup-0002-ds01.txt"
# aquifer_file = "aqu_temp.txt"

features = {"aquifer_depth": "aquifer_depth"}

data_path = os.path.join(
    os.path.dirname(__file__),
    "..",
    "..",
    "data",
    "raw",
)
file_path = os.path.join(data_path, "aquifer_depth_tesauro_etal.txt")
assert os.path.isfile(file_path), f"Aquifer depth file {file_path} does not exist."

aquifer_depth_coords = ["x", "y"]
crs = 4326


def get_data(cutout, *args, **kwargs):
    """
    Cuts out sediment thickness for cutout region.

    Args:
        cutout(Cutout or GeoCutout): requires attribute 'coords'

    """

    coords = cutout.coords

    data = pd.read_csv(
        file_path,
        skiprows=1,
        sep="\t",
        header=None,
    )
    data.columns = [
        "X",
        "Y",
        "UC",
        "LC",
        "AVCRUST",
        "Topo",
        "Basement",
        "UC/LC",
        "Moho",
    ]

    x_mesh, y_mesh = np.meshgrid(cutout.coords["x"].values, cutout.coords["y"].values)

    grid_values = griddata(
        data[["X", "Y"]].to_numpy(), data["Basement"].values, (x_mesh, y_mesh)
    )

    ds = xr.Dataset(
        data_vars=dict(
            aquifer_depth=(aquifer_depth_coords, grid_values),
        ),
        coords={
            name: vals for (name, vals), _ in zip(coords.indexes.items(), range(2))
        },
    )

    ds = ds.assign_coords(lon=ds.coords["x"], lat=ds.coords["y"])

    return ds
