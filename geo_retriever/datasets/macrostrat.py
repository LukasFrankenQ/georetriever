import geopandas as gpd
import requests
import numpy as np
import xarray as xr
from io import StringIO
from PIL import ImageColor

# from geo_retriever.utils import Lith
from utils import Lith
# from gis import maybe_swap_spatial_dims

features = {"lithology": "lithology"}
lith_coords = ["x", "y"]
crs = 4326

'''
def _rename_and_clean_coords(ds, add_lon_lat=True):
    """Rename 'longitude' and 'latitude' columns to 'x' and 'y' and fix roundings.
    Optionally (add_lon_lat, default:True) preserves latitude and longitude
    columns as 'lat' and 'lon'.
    """
    ds = ds.rename({"longitude": "x", "latitude": "y"})
    # round coords since cds coords are float32 which would lead to mismatches
    ds = ds.assign_coords(
        x=np.round(ds.x.astype(float), 5), y=np.round(ds.y.astype(float), 5)
    )
    ds = maybe_swap_spatial_dims(ds)
    if add_lon_lat:
        ds = ds.assign_coords(lon=ds.coords["x"], lat=ds.coords["y"])
    return ds
'''

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