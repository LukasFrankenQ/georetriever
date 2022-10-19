import SoilFuncs
import BoreholeFuncs
import macrostratAPI
import streamlit as st
import pandas as pd
import numpy as np

st.title("GSHP Borehole Depth Calculator")
st.header("Location")


inputLocation = st.text_input("Input your nearest city: ")
latlng = macrostratAPI.getLatLng(inputLocation)

inputlat = st.number_input("latitude: ",value = latlng[1])
inputLng = st.number_input("longitude: ", value = latlng[0])

# df = pd.DataFrame(
#      [inputlat, inputLng],
#      columns=['lat', 'lon'])

# st.map(df)

rock = macrostratAPI.GetMajorGeology(inputlat, inputLng)

st.text("The ground type is: " + rock)

# Get user inputs
st.header("House Inputs")
inputFloorArea = st.number_input("Input house floor area (m^2): ",0)
inputHouseAge = st.number_input("Input house Age (years): ",5)

# calculate values
heatExtraction = SoilFuncs.getheatExtraction(rock)
heatloss = BoreholeFuncs.getHeatLoss(inputHouseAge)
peakLoad = BoreholeFuncs.getPeakHeatLoad(inputFloorArea,heatloss)
bhDepth = BoreholeFuncs.getBoreholeDepth(heatExtraction, peakLoad)
cost = bhDepth*45
boreHoleDepth = str("{:.2f}".format(bhDepth))
cost = str("{:.2f}".format(cost))

st.header("Results")
st.text("Required borehole depth is: " + boreHoleDepth + "m")
st.text("Hole drilling cost: £" + cost)