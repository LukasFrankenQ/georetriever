import pandas as pd
# import pint

houseAgeData = {
    0:41,
    10:45,
    20:55,
    40:60,
    60:70,
}

def getBoreholeDepth(heatExtraction, peakHeatLoad):
    return peakHeatLoad/heatExtraction

def getPeakHeatLoad(floorArea, heatLoss):
    return floorArea*heatLoss

def getHeatLoss(x):
    return houseAgeData.get(x, houseAgeData[min(houseAgeData.keys(), key=lambda k: abs(k-x))])



