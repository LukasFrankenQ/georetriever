import geopandas as gpd
import requests
import numpy as np
import xarray as xr
from io import StringIO

# static_features = dict(lithography="lithography"])
features = {"lithology": "lithology"}
crs = 4326


def get_data(geocutout,
             feature,
             tmpdir=None,
             lock=None,
             **creation_parameters,
             ):
    
    coords = geocutout.coords

    x, y, _ = geocutout.coords.indexes.values()
    x, y = np.meshgrid(x, y)

    grid = gpd.GeoDataFrame(geometry=gpd.points_from_xy(x.flatten(), y.flatten()))

    grid["lng"] = x.flatten()
    grid["lat"] = y.flatten()
    grid["lith"] = (np.ones(len(grid)) * (-1)).astype("int")

    request_params = dict(
        format="geojson_bare",
    )
    api_link = "https://macrostrat.org/api/geologic_units/map"

    for idx, row in grid.iterrows():
        
        if not grid.loc[idx, "lith"] == -1:
            continue

        request_params.update(lat=row.lat)
        request_params.update(lng=row.lng)

        result = requests.get(api_link, params=request_params)
        
        result = result.content 
        result = StringIO(str(result, "utf-8"))
        result = gpd.read_file(result)

        try:
            result = result.loc[result["lith"].str.contains("Major")].iloc[0] 
        except IndexError:        
            result = result.iloc[0]

        polygon = result.loc["geometry"]
        lith = result.loc["lith"]

        assign_mask = grid["geometry"].within(polygon)
        grid.loc[assign_mask, "lith"] = lith

    grid = grid["lith"].to_numpy().reshape(x.shape)

    grid = xr.Dataset(
        data_vars=dict(
            lithology=(list(coords.dims)[:2], grid),
        ), 
        coords={
        name: vals
        for (name, vals), _ in zip(coords.indexes.items(), range(2))}
    )
    grid = grid.assign_coords(lon=grid.coords["x"], lat=grid.coords["y"])

    return grid 