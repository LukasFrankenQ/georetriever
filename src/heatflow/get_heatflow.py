import os
from sklearn.neighbors import KDTree
import geopandas as gpd
import numpy as np


def get_heatflow(coords):
    '''
    Obtains the heatflow from the closest datapoint from the heatflow dataset
    
    Args:
        coords(tuple): lon lat pair 
    ''' 
    
    lng, lat = coords
    
    gdf = gpd.read_file(os.path.join(os.getcwd(), 'data', 'heatflow.geojson'))        

    # print(gdf.head())
    tree = KDTree(gdf[['lng', 'lat']].to_numpy(), leaf_size=1)

    _, idx = tree.query(np.array([[lng, lat]]))
    idx = idx[0,0]
    
    return gdf.at[idx, 'q']