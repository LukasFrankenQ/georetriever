import os
from sklearn.neighbors import KDTree
import geopandas as gpd
import numpy as np
from pathlib import Path

ROOT_DIR = Path(os.path.dirname(os.path.abspath(__file__)))

def get_heatflow(coords):
    '''
    Obtains the heatflow from the closest datapoint from the heatflow dataset
    
    Args:
        coords(tuple): lon lat pair 
    ''' 
    
    lng, lat = coords
    
    gdf = gpd.read_file(os.path.join(ROOT_DIR / 'data' / 'heatflow.geojson'))        

    tree = KDTree(gdf[['lng', 'lat']].to_numpy(), leaf_size=1)

    _, idx = tree.query(np.array([[lng, lat]]))
    idx = idx[0,0]
    
    return gdf.at[idx, 'q']