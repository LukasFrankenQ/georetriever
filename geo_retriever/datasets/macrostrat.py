import geopandas as gpd
import requests
import numpy as np
import xarray as xr
from io import StringIO
from PIL import ImageColor

from utils import Lith

features = {"lithology": "lithology"}
lith_coords = ["x", "y"]
crs = 4326


def get_data(geocutout,
             args,
             **kwargs,
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

        request_params.update(dict(lat=row.lat, lng=row.lng))

        result = requests.get(api_link, params=request_params)
        
        result = result.content 
        result = StringIO(str(result, "utf-8"))
        result = gpd.read_file(result)

        lith = Lith()
        lith, best_info = lith.interpret_macrostrat(result["lith"], 
                                                    return_best_info=True)

        try:
            color = result.iloc[best_info].loc["color"]
            lith.colors = ImageColor.getcolor(color, "RGB")
        except TypeError: 
            pass
                
        polygon = result.iloc[best_info].loc["geometry"]

        assign_mask = grid["geometry"].within(polygon)
        grid.loc[assign_mask, "lith"] = lith

    grid = grid["lith"].to_numpy().reshape(x.shape[::-1])

    ds = xr.Dataset(
        data_vars=dict(
            lithology=(lith_coords, grid),
        ), 
        coords={
        name: vals
        for (name, vals), _ in zip(coords.indexes.items(), range(2))}
    )
    ds = ds.assign_coords(lon=ds.coords["x"], lat=ds.coords["y"])

    return ds