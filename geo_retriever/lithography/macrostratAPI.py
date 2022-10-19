from cmath import nan
import requests
import contextily as ctx
import matplotlib.pyplot as plt
import json
import re

def getLatLng(loc):
    geology_tiles = 'https://tiles.macrostrat.org/carto/{z}/{x}/{y}.png'
    basemap = ctx.providers.Stamen.Toner
    location = "{0}, UK".format(loc)

    place = ctx.Place(location, source=basemap)
    return [place.longitude, place.latitude]
    lng = place.longitude
    lat = place.latitude

def GetMajorGeology(lat, lng):
    # res = getLatLng(loc)
    # lng = res[0]
    # lat = res[1] 
    # print(lat, lng)

    res = requests.get("https://macrostrat.org/api/geologic_units/map",params={'lat':lat, 'lng':lng, 'format':"geojson_bare"})
    
    major = ""
    options = []

    for feature in json.loads(res.text)['features']:
        lith = feature['properties']['lith']
        try:
            major = re.search(r'Major:{(\w+)}',lith).groups()[0]
        except:
            options.append(lith.split(',')[0])

    if major != "":
        return major
    else:
        return options[-1]
