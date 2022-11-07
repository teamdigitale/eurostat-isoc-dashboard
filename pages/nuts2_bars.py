# -*- coding: utf-8 -*-
"""
@author: fv456
"""
import streamlit as st

import pandas as pd
import pickle
import plotly.express as px

import dtd_streamlit_utils as utils

# %% Streamlit app


@st.cache
def get_eurostat_data_2019():
    # Database version 2022-3-25, preprocessing version 2022-06-01
    with open("data/eurostat_NUTS2_v220601.pickle", "rb") as f:
        df = pickle.load(f)
    df["VALUE"] = df["VALUE"] * 100.0
    df["VAR_AND_BRK"] = df["VARIABLE"] + "-" + df["BREAKDOWN_TYPE"]
    df["CAPTION_ALL"] = df["VARIABLE_CAPTION"] + " - " + df["BREAKDOWN_CAPTION"]

    # è l'unico anno tra i più recenti che abbia sufficienti dati nel db corrente
    df = df[df["YEAR"] == 2019]

    df = df[df["UNIT"].isin(["PC_IND", "PC_HH"])]
    df["AREA_TYPE"] = [
        "macro" if len(brk) == 3 else "reg" for brk in df["BREAKDOWN_TYPE"]
    ]
    return df


def app():

    df_all = get_eurostat_data_2019()

    vars_and_captions = df_all[["VARIABLE", "VARIABLE_CAPTION"]].drop_duplicates()
    vars_and_captions = vars_and_captions.set_index("VARIABLE")  # .sort_index()
    vars_and_captions = vars_and_captions["VARIABLE_CAPTION"].to_dict()

    # Base per le variabili: tutte le disponibili nel dataset
    ALL_VARS = sorted(df_all["VARIABLE"].unique())

    ALL_BRKS = pd.Series(
        df_all["BREAKDOWN_TYPE"].unique()
    )  # TODO: rimuovere il brk Y0_15, solo pochi Paesi lo monitorano

    SORTED_BRKS = [  # "ITH", "ITI", "ITF", "ITG", # Macro regioni, si veda sotto
        # Nord-Ovest
        "ITC",
        "ITC1",
        "ITC2",
        "ITC3",
        "ITC4",
        # Nord-Est (Province Trento e Bolzano separate)
        "ITH",
        "ITH1",
        "ITH2",
        "ITH3",
        "ITH4",
        "ITH5",
        # Centro
        "ITI",
        "ITI1",
        "ITI2",
        "ITI3",
        "ITI4",
        # Sud
        "ITF",
        "ITF1",
        "ITF2",
        "ITF3",
        "ITF4",
        "ITF5",
        "ITF6",
        # Isole
        "ITG",
        "ITG1",
        "ITG2",
    ]

    temp = (
        df_all[["BREAKDOWN_TYPE", "BREAKDOWN_CAPTION"]]
        .drop_duplicates()
        .set_index("BREAKDOWN_TYPE")
    )
    SORTED_BRKS_CAPTIONS = temp.loc[SORTED_BRKS]["BREAKDOWN_CAPTION"]

    # ---- MAIN PAGE START
    st.title("Eurostat ISOC-I variables with NUTS2 breakdown (year 2019)")
    st.header("Italian regions comparison tool")
    st.write(
        "Source data link: https://ec.europa.eu/eurostat/web/digital-economy-and-society/data/comprehensive-database"
    )
    st.write("Statistics on Households/Individuals, db version 25 March 2022")
    st.write(
        "Web app source code link: https://github.com/teamdigitale/eurostat-isoc-dashboard/pages/nuts2_bars.py"
    )

    # --------------------------------------------------------------------------------

    if len(df_all) == 0:
        st.markdown("WARNING: filter resulted in **NO DATA**.")
        st.write()
        return

    for var in ALL_VARS:
        try:
            if var == "sampleh" or var == "samplep":
                continue

            st.subheader(f"Variable {vars_and_captions[var]} [{var}]")
            df_viz = df_all[(df_all.VARIABLE == var)]

            fig = px.bar(df_viz, x="BREAKDOWN_CAPTION", y="VALUE", color="AREA_TYPE")
            fig = fig.update_xaxes(
                categoryorder="array", categoryarray=SORTED_BRKS_CAPTIONS
            )
            utils.st_create_download_btn(
                fig, "Download chart below", f"boxplot_{var}.html"
            )
            st.plotly_chart(fig, use_container_width=True)

        except:
            print(f"Problems with variable {var}")

    print("Eurostat NUTS2 navigation page loaded.")


# %% Exec with file
if __name__ == "__main__":
    print("Eurostat ISOC-I NUTS2 data navigation app, executed as main")
    st.set_page_config(layout="wide")
    app()
