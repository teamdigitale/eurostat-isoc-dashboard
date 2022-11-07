# -*- coding: utf-8 -*-
"""
@author: fv456
"""
import streamlit as st

import numpy as np
import pandas as pd
import pickle
import plotly.express as px
import dtd_streamlit_utils as utils


# %% Streamlit app


def app():

    with open("data/eurostat_ISOC_BDE15CUA_v220325.pickle", "rb") as f:
        df = pickle.load(f)
    df["VALUE"] = df["VALUE"] * 100.0

    df["VAR_AND_BRK"] = df["VARIABLE"] + "-" + df["BREAKDOWN_TYPE"]
    df["CAPTION_ALL"] = df["VARIABLE_CAPTION"] + " - " + df["BREAKDOWN_CAPTION"]

    year = st.sidebar.selectbox("Year?", [2019, 2020, 2021], index=2)

    df_ita_YY = df.query(f"YEAR=={year} and GEO=='IT'")[["VAR_AND_BRK", "VALUE"]]
    df_ita_YY.columns = ["VAR_AND_BRK", "VAL_IT"]
    df_deltas = df_ita_YY[["VAR_AND_BRK"]].copy(deep=True)

    EU_COUNTRIES = {
        "EU27_2020": "European Average",
    } | utils.get_eu_countries(eu_union=True, eu_candidates=True, eu_other=False)

    country = st.sidebar.selectbox(
        "Compare Italy with..?",
        EU_COUNTRIES.keys(),
        index=0,
        format_func=lambda id: EU_COUNTRIES[id],
    )

    COLNAME = f"DELTA_{country}"

    df_country_YY = df.query(f"YEAR=={year} and GEO=='{country}'")[
        ["VAR_AND_BRK", "VALUE"]
    ]
    df_country_YY.columns = ["VAR_AND_BRK", f"VAL_{country}"]
    df_temp = pd.merge(df_ita_YY, df_country_YY)
    df_temp[COLNAME] = df_temp["VAL_IT"] - df_temp[f"VAL_{country}"]
    df_deltas = pd.merge(df_deltas, df_temp[["VAR_AND_BRK", COLNAME]])

    df_deltas = df_deltas.sort_values(COLNAME)
    df_deltas = df_deltas.dropna()
    df_temp = df[
        [
            "VAR_AND_BRK",
            "CAPTION_ALL",
            "VARIABLE_CAPTION",
            "BREAKDOWN_CAPTION",
            "VARIABLE",
            "BREAKDOWN_TYPE",
        ]
    ].drop_duplicates()
    df_deltas = pd.merge(df_deltas, df_temp, on="VAR_AND_BRK")

    v_max_range = max(abs(df_deltas[COLNAME]))
    v_max = max(df_deltas[COLNAME])
    v_min = min(df_deltas[COLNAME])

    threshold_min, threshold_max = st.sidebar.slider(
        "Threshold for delta", min_value=v_min, max_value=v_max, value=(v_min, v_max)
    )

    ALL_VARS = np.sort(df_deltas["VARIABLE"].unique())
    selected_variables = st.sidebar.multiselect(
        "Selected variables:", ALL_VARS, ALL_VARS
    )
    df_deltas = df_deltas[df_deltas["VARIABLE"].isin(selected_variables)]

    filter_var_d = st.sidebar.text_input("Filter variables descriptions").lower()
    df_deltas = df_deltas[
        df_deltas["VARIABLE_CAPTION"].str.lower().str.contains(filter_var_d)
    ]

    filter_brk = st.sidebar.text_input("Filter breakdowns names").lower()
    df_deltas = df_deltas[
        df_deltas["BREAKDOWN_TYPE"].str.lower().str.contains(filter_brk)
    ]

    filter_brk_d = st.sidebar.text_input("Filter breakdowns descriptions").lower()
    df_deltas = df_deltas[
        df_deltas["BREAKDOWN_CAPTION"].str.lower().str.contains(filter_brk_d)
    ]

    # ---- MAIN PAGE START
    st.title("Digital skills: internet use and activities")
    st.header("Eurostat table BDE15CUA")
    st.write(
        "Source table link: http://appsso.eurostat.ec.europa.eu/nui/show.do?dataset=isoc_bde15cua&lang=en"
    )
    st.write(
        "Web app source code link: https://github.com/teamdigitale/eurostat-isoc-dashboard/blob/main/pages/bde15cua_treemaps.py"
    )

    # --------------------------------------------------------------------------------

    if len(df_deltas) == 0:
        st.markdown("WARNING: filter resulted in **NO DATA**.")
        st.write()
        return

    df_viz = df_deltas.query(
        f"{COLNAME} <= {threshold_max} and {COLNAME} >= {threshold_min}"
    )
    n_comb = len(df_viz)
    fig = px.treemap(
        df_viz.head(n_comb),
        path=[px.Constant("EUROSTAT"), "VARIABLE", "BREAKDOWN_TYPE"],
        values=px.Constant(1),  # values='pop',
        color=COLNAME,
        hover_data=["VARIABLE_CAPTION", "BREAKDOWN_CAPTION"],
        color_continuous_scale="RdBu",
        height=600,
        title=f"Variable -> breakdown combinations",
        range_color=[-v_max_range, v_max_range],
    )  # per ottenere range simmetrico (bianco sullo zero)
    st.plotly_chart(fig, use_container_width=True)
    utils.st_create_download_btn(
        fig,
        "Download filtered treemap VAR->BRK above (HTML file)",
        "eurostat_dsk_var_brk_treemap.html",
    )

    df_viz = df_deltas.query(
        f"{COLNAME} <= {threshold_max} and {COLNAME} >= {threshold_min}"
    )
    n_comb = len(df_viz)
    fig = px.treemap(
        df_viz.head(n_comb),
        path=[px.Constant("EUROSTAT"), "BREAKDOWN_TYPE", "VARIABLE"],
        values=px.Constant(1),  # values='pop',
        color=COLNAME,
        hover_data=["VARIABLE_CAPTION", "BREAKDOWN_CAPTION"],
        color_continuous_scale="RdBu",
        height=700,
        title=f"Breakdown -> variable combinations",
        range_color=[-v_max_range, v_max_range],
    )  # per ottenere range simmetrico (bianco sullo zero)
    st.plotly_chart(fig, use_container_width=True)
    utils.st_create_download_btn(
        fig,
        "Download filtered treemap BRK->VAR above (HTML file)",
        "eurostat_dsk_brk_var_treemap.html",
    )

    print("Eurostat table BDE15CUA navigation page loaded.")


# %% Exec with file
if __name__ == "__main__":
    print("Eurostat data navigation app, executed as main")
    st.set_page_config(layout="wide")
    app()
