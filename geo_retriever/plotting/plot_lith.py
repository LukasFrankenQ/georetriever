import numpy as np
from itertools import product
import matplotlib.pyplot as plt


def plot_lith(liths):
    """
    Creates a plot of lithologies
    
    Args:
        liths(xr.DataArray): matrix of lithology objects
    """ 

    coords = liths.coords

    x = coords["x"].to_numpy()
    y = coords["y"].to_numpy()
   
    extent = [x.min(), x.max(), y.min(), y.max()]  
   
    liths_np = liths.to_numpy()  
    image = np.zeros(tuple(list(liths_np.shape)+[3]))
    
    for i, j in product(range(image.shape[0]), range(image.shape[1])):
        image[i,j] = liths_np[i,j].colors
    
    image = image.astype(int)
    fig, ax = plt.subplots(1, 1, figsize=(16, 16))
    ax.imshow(image[::-1], extent=extent)
    plt.show() 