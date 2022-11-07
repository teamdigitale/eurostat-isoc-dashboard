# -*- coding: utf-8 -*-
"""
@author: fv456
"""
import pandas as pd
import streamlit as st
import plotly.express as px
import pickle

import dtd_streamlit_utils as utils


# %% Streamlit app


@st.cache
def get_countries_delta_data(
    country_B: str, year_b: int, year: int, delta_colname: str
):  # TODO: ristrutturare questa funzione

    # Database version 2022-3-25, preprocessing version 2022-4-20
    with open("data/eurostat_DSK_v220420.pickle", "rb") as f:
        df = pickle.load(f)
    df["VALUE"] = df["VALUE"] * 100.0
    df["VAR_AND_BRK"] = df["VARIABLE"] + "-" + df["BREAKDOWN_TYPE"]
    df["CAPTION_ALL"] = df["VARIABLE_CAPTION"] + " - " + df["BREAKDOWN_CAPTION"]

    df_ita_YY = df.query(f"YEAR=={year} and GEO=='IT'")[["VAR_AND_BRK", "VALUE"]]
    df_ita_YY.columns = ["VAR_AND_BRK", "VAL_IT"]

    # Utilizziamo come base per la differenza le combinazioni var/brk disponibili per
    # l'Italia nell'anno selezionato
    df_deltas = df_ita_YY[["VAR_AND_BRK"]].copy(deep=True)

    df_country_YY = df.query(f"YEAR=={year_b} and GEO=='{country_B}'")[
        ["VAR_AND_BRK", "VALUE"]
    ]
    df_country_YY.columns = ["VAR_AND_BRK", "VAL_VS"]
    df_temp = pd.merge(df_ita_YY, df_country_YY)
    df_temp[delta_colname] = df_temp["VAL_IT"] - df_temp["VAL_VS"]

    df_deltas = pd.merge(df_deltas, df_temp[["VAR_AND_BRK", delta_colname]])

    df_deltas = df_deltas.sort_values(delta_colname)
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

    return df_deltas


def app():

    year = st.sidebar.selectbox("Year?", [2019, 2020, 2021], index=0)

    EU_COUNTRIES = {
        "EU27_2020": "European Average",
    } | utils.get_eu_countries(eu_union=True, eu_candidates=True, eu_other=False)

    country = st.sidebar.selectbox(
        "Compare Italy in selected year with..?",
        EU_COUNTRIES,
        index=0,
        format_func=lambda id: EU_COUNTRIES[id],
    )

    year_b = st.sidebar.selectbox("Which year?", [2019, 2020, 2021], index=0)

    COLNAME = f"DELTA_{country}"
    df_deltas = get_countries_delta_data(
        str(country), int(str(year_b)), int(str(year)), COLNAME
    )

    # Filtraggi sulle soglie dei valori di confronto
    v_max_range = max(abs(df_deltas[COLNAME]))
    v_max = max(df_deltas[COLNAME])
    v_min = min(df_deltas[COLNAME])
    threshold_min, threshold_max = st.sidebar.slider(
        "Threshold for delta", min_value=v_min, max_value=v_max, value=(v_min, v_max)
    )
    df_deltas = df_deltas.query(
        f"{COLNAME} <= {threshold_max} and {COLNAME} >= {threshold_min}"
    )

    # Base per le variabili: tutte le disponibili nel dataset
    ALL_VARS = df_deltas["VARIABLE"].unique()
    ALL_VARS.sort()

    # Tipo delle variabili: sorgente base, DSK calcolate, oppure entrambe?
    variables_type = st.sidebar.radio(
        "Select variable type:", ("All", "Source", "Calculated"), index=1
    )
    temp = pd.Series(ALL_VARS)
    if variables_type == "Source":
        ALL_VARS = temp[~temp.str.contains("_DSK")]
    elif variables_type == "Calculated":
        ALL_VARS = temp[temp.str.contains("_DSK")]
    del temp

    # Filtri sulle variabili
    selected_variables = st.sidebar.multiselect(
        "Selected variables:", ALL_VARS, ALL_VARS
    )
    df_deltas = df_deltas[df_deltas["VARIABLE"].isin(selected_variables)]
    filter_var_d = st.sidebar.text_input("Filter variables descriptions").lower()
    df_deltas = df_deltas[
        df_deltas["VARIABLE_CAPTION"].str.lower().str.contains(filter_var_d)
    ]

    # Filtri sui breakdown
    filter_brk = st.sidebar.text_input("Filter breakdowns names").lower()
    df_deltas = df_deltas[
        df_deltas["BREAKDOWN_TYPE"].str.lower().str.contains(filter_brk)
    ]
    filter_brk_d = st.sidebar.text_input("Filter breakdowns descriptions").lower()
    df_deltas = df_deltas[
        df_deltas["BREAKDOWN_CAPTION"].str.lower().str.contains(filter_brk_d)
    ]

    # ---- MAIN PAGE START
    st.title("Digital skills")
    st.header("Comparison tool")
    st.write(
        "Source data link: https://ec.europa.eu/eurostat/web/digital-economy-and-society/data/comprehensive-database"
    )
    st.write("Statistics on Households/Individuals, db version 25 March 2022")
    st.write(
        "Web app source code link: https://github.com/teamdigitale/eurostat-isoc-dashboard/pages/digital_skills_treemaps.py"
    )

    # --------------------------------------------------------------------------------

    if len(df_deltas) == 0:
        st.markdown("WARNING: filter resulted in **NO DATA**.")
        st.write()
        return

    fig = px.treemap(
        df_deltas,
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

    fig = px.treemap(
        df_deltas,
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

    print("Eurostat DSK navigation page loaded.")


# %% Exec with file
if __name__ == "__main__":
    print("Eurostat data navigation app, executed as main")
    st.set_page_config(layout="wide")
    app()
