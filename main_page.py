# -*- coding: utf-8 -*-
"""
@author: fv456
"""

import streamlit as st
import plotly.express as px
import dtd_streamlit_utils as utils


st.header("Eurostat Digital economy and society Dashboard")

# st.markdown("open README.MD ?")

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

# def main_page():
#     st.markdown("# Main page 🎈")
#     st.sidebar.markdown("# Main page 🎈")

# def page2():
#     st.markdown("# Page 2 ❄️")
#     st.sidebar.markdown("# Page 2 ❄️")

# def page3():
#     st.markdown("# Page 3 🎉")
#     st.sidebar.markdown("# Page 3 🎉")

# page_names_to_funcs = {
#     "Main Page": main_page,
#     "Page 2": page2,
#     "Page 3": page3,
# }

# selected_page = st.sidebar.selectbox("Select a page", page_names_to_funcs.keys())
# page_names_to_funcs[selected_page]()
