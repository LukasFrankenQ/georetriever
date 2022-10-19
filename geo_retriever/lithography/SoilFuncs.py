import pandas as pd
rocks = {'siliciclastic':50,
        'gravel':76,
        'sand':60,
        'silt':34,
        'mud':28,
        'claystone':50,
        'mudstone':50,
        'shale':50,
        'siltstone':50,
        'sandstone':43,
        'limestone':34,
        'basalt':33,
        'granite':35,
        'gneiss':40,
        }

def getheatExtraction(x):
    return rocks.get(x,60)




