import os
import re
from pathlib import Path
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
plt.style.use('bmh')

def clean_heatflow_data(df):
    '''
    !!! 
    Taylored to the error present in the heatflow dataset
    https://ihfc-iugg.org/products/global-heat-flow-database/data 
    !!!

    Iterates over rows, ensures lon lat data is float

    Args:
        df(pd.DataFrame): data of heatflow, expects columns 'q', 'lng', 'lat' 

    '''
    for col in ['lng', 'lat']:

        keepmask = pd.Series([True for _ in range(len(df))], index=df.index)

        for i, row in df.iterrows():
            if not isinstance(row[col], float):

                coord = re.sub(r'[^0-9.]', '', row[col])

                try:
                    coord = float(coord)
                    df.at[i, col] = coord
                except ValueError:
                    keepmask.at[i] = False


        df = df.loc[keepmask]

    df = df.loc[df['q'] < 100]
    df = df.loc[df['q'] > 0]

    return df
    

if __name__ == '__main__':

    file1 = 'IHFC_2021_GHFDB.csv'
    file2 = 'IHFC_2021_GHFDB.xlsx'

    base = Path(os.getcwd()) / 'data'

    df = pd.read_csv(base / file1, encoding='ISO-8859–1', on_bad_lines='skip', sep=';')
    df = df[['q', 'lat', 'lng']]

    df = clean_heatflow_data(df)

    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))

    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.lng, df.lat))
    fig, ax = plt.subplots(1, 1, figsize=(16, 13))
    world.plot(ax=ax)
    gdf.plot(ax=ax, column='q', s=20)
    ax.set_axisbelow(True)
    plt.show()

    gdf.to_file(os.path.join(os.getcwd(), 'data', 'heatflow.geojson'), driver='GeoJSON')