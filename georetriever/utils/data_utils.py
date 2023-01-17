import numpy as np
from shapely.geometry import Polygon
import geopandas as gpd


def polygons_to_xarray(da, gdf, col):
    """
    Constructs box-shape polygons around points in da (xr.DataArray).
    Conducts spatial join, to get for each box the polygons in gdf
    that have overlap
    Then iterates over the boxes, to each assigning the weighted
    average of gdf[col] with weights determined by intersection area
    per polygon.

    Args:
        da(xr.DataArray): only coords will be considered
        gdf(gpd.GeoDataFrame): data with polygons in area of coords
        col(str): column of gdf from which numeric values should be averaged

    Returns:
        xr.DataArray
    """

    coords = da.coords

    x = list(coords.values())[0].values
    y = list(coords.values())[1].values

    x_offset = (x[1] - x[0]) / 2
    y_offset = (y[1] - y[0]) / 2

    x, y = np.meshgrid(x, y)

    x = x.flatten()
    y = y.flatten()

    lower_lefts = np.vstack([x - x_offset, y - y_offset]).T
    lower_rights = np.vstack([x + x_offset, y - y_offset]).T
    upper_rights = np.vstack([x + x_offset, y + y_offset]).T
    upper_lefts = np.vstack([x - x_offset, y + y_offset]).T

    boxes = [
        Polygon([ll, lr, ur, ul])
        for ll, lr, ur, ul in zip(lower_lefts, lower_rights, upper_rights, upper_lefts)
    ]
    arr_as_df = gpd.GeoDataFrame(
        {
            "geometry": boxes,
            "center_x": x,
            "center_y": y,
        }
    )
    arr_as_df["saveindex"] = arr_as_df.index
    arr_as_df[col] = np.zeros(len(arr_as_df))
    overlaps = arr_as_df.sjoin(gdf, predicate="overlaps", how="left")

    def get_weighted_mean(row):

        subset = gdf.loc[overlaps.loc[row.saveindex].index_right]
        if isinstance(subset.geometry, Polygon):
            return getattr(subset, col)

        weights = np.array(
            [p.intersection(row.geometry).area for _, p in subset.geometry.items()]
        )
        if weights.sum() > 0:
            weights = weights / weights.sum()
        return np.inner(weights, subset[col])

    arr_as_df[col] = arr_as_df.apply(lambda row: get_weighted_mean(row), axis=1)

    da.data = arr_as_df[col].values.reshape(da.shape)

    return da
