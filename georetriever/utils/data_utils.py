import numpy as np
import xarray as xr
import pandas as pd
from shapely.geometry import Polygon, MultiPolygon
import geopandas as gpd


def polygons_to_xarray(da, gdf, cols):
    """
    Constructs box-shape polygons around points in da (xr.DataArray).
    Conducts spatial join, to get for each box the polygons in gdf
    that have overlap
    Then iterates over the boxes, to each assigning the weighted
    average of gdf[col] with weights determined by intersection area
    per one polygon.
    Conducts all math in the respective UTM zone, to accurately
    respect distances.

    Args:
        da(xr.DataArray): only coords will be considered
        gdf(gpd.GeoDataFrame): data with polygons in area of coords
        cols(str or List[str]): columns of gdf that will be obtained

    Returns:
        xr.DataArray
    """

    if isinstance(cols, str):
        cols = [cols]

    coords = da.coords

    x_range = list(coords.values())[0].values
    y_range = list(coords.values())[1].values

    x_offset = (x_range[1] - x_range[0]) / 2
    y_offset = (y_range[1] - y_range[0]) / 2

    x, y = np.meshgrid(x_range, y_range)

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
        },
        crs="EPSG:4326",
    )
    arr_as_df["saveindex"] = arr_as_df.index
    arr_as_df[cols] = np.zeros((len(arr_as_df), len(cols)))

    overlaps = arr_as_df.sjoin(gdf, predicate="overlaps", how="left")

    def get_weighted_mean(row):

        try:
            subset = gdf.loc[overlaps.loc[row.saveindex].index_right]
        except KeyError:
            values = np.zeros(len(cols))
            values[:] = np.nan
            return values

        if isinstance(subset.geometry, Polygon) or isinstance(
            subset.geometry, MultiPolygon
        ):
            return subset.loc[cols].values

        weights = np.array(
            [p.intersection(row.geometry).area for _, p in subset.geometry.items()]
        )
        values = subset[cols].values

        if weights.sum() > 0:
            weights = weights / weights.sum()
        return np.matmul(values.T, weights)

    arr_as_df[cols] = arr_as_df.apply(
        lambda row: pd.Series(get_weighted_mean(row), index=cols), axis=1
    )

    xr_kwargs = dict(
        coords=[y_range, x_range],
        dims=["y", "x"],
    )

    rev_shape = tuple(list(da.shape)[::-1])

    dataset = xr.DataArray(
        # arr_as_df[cols[0]].values.reshape(da.shape),
        arr_as_df[cols[0]].values.reshape(rev_shape),
        **xr_kwargs
    ).to_dataset(name=cols[0])

    for col in cols[1:]:
        dataset[col] = xr.DataArray(
            # arr_as_df[col].values.reshape(da.shape),
            arr_as_df[col].values.reshape(rev_shape),
            **xr_kwargs
        )

    return dataset
