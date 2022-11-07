# -*- coding: utf-8 -*-
"""
@author: fv456
"""

import streamlit as st
import plotly.express as px
import dtd_streamlit_utils as utils


st.header("Eurostat Digital economy and society Dashboard")

st.write(
    "Analytics dashboard that uses portions of Eurostat data downloadable from "
    "[this link](https://ec.europa.eu/eurostat/web/digital-economy-and-society/data/comprehensive-database)."
)

st.write("Use left menu to navigate the following pages:")

st.markdown(
    "- **bde15cua treemaps:** Compare Italy with other EU countries on "
    "internet use and activities in households and individuals, using treemaps."
)

st.markdown(
    "- **digital skills boxplots:** Compare Italy with other EU countries on "
    "digital skills in households and individuals, using boxplots."
)

st.markdown(
    "- **digital skills treemaps:** Compare Italy with other EU countries on "
    "digital skills in households and individuals, using treemaps."
)

st.markdown(
    "- **ict in enterprises:** Compare Italy with other EU countries on "
    "ICT use in enterprises, using treemaps."
)

st.markdown(
    "- **nuts2 bars:** Compare all Italian regions data (NUTS2) available "
    "in Eurostat's database 'Statistics on households / individuals'"
)
