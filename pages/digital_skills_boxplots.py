# -*- coding: utf-8 -*-
"""
@author: fv456
"""
import streamlit as st

import pandas as pd
import pickle
import plotly.graph_objects as go

import dtd_streamlit_utils as utils

# %% Streamlit app


def create_boxplot(df_all, variable_name: str) -> go.Figure:

    df_box = df_all[(df_all.VARIABLE == variable_name)]

    fig = go.Figure()
    fig.update_layout(showlegend=False)
    fig = fig.update_layout(height=600)

    # Ciclo su tutti i breakdown      # TEST: brk = 'Y16_24'
    for brk in df_box.BREAKDOWN_TYPE.unique():  # TODO: rivedere l'ordinamento

        try:
            df = df_box[df_box["BREAKDOWN_TYPE"] == brk]

            # Aggiungo un boxplot per l'indicatore
            fig.add_trace(
                go.Box(
                    y=df["VALUE"],
                    name=brk,
                    marker_color="#1f77b4",
                    boxmean=True,  # represent mean
                )
            )

            # Punto blu per ogni Paese
            fig.add_trace(
                go.Scatter(
                    x=df["BREAKDOWN_TYPE"],
                    y=df["VALUE"],
                    line_color="#0f5794",
                    mode="markers",
                    hovertext=df["GEO_CAPTION"],
                )
            )

            # Punto rosso sul valore dell'Italia
            val_italy = df[df["GEO"] == "IT"]["VALUE"].item()
            fig.add_trace(
                go.Scatter(
                    x=df["BREAKDOWN_TYPE"],
                    y=[val_italy],
                    line_color="red",
                    hovertext=["Italy"],
                )
            )

        except:
            print(f"Problem with breakdown {brk}. Skipping..")

    return fig


@st.cache
def get_eurostat_data():

    COUNTRIES = utils.get_eu_countries()

    # Database version 2022-3-25, preprocessing version 2022-4-20
    with open("data/eurostat_DSK_v220420.pickle", "rb") as f:
        df = pickle.load(f)

    df["VALUE"] = df["VALUE"] * 100.0
    df["VAR_AND_BRK"] = df["VARIABLE"] + "-" + df["BREAKDOWN_TYPE"]
    df["CAPTION_ALL"] = df["VARIABLE_CAPTION"] + " - " + df["BREAKDOWN_CAPTION"]

    # Mantengo solo i Paesi oggetto di analisi (rimuove anche aggregazioni come EU15, ecc..)
    df = df[df.GEO.isin(COUNTRIES)]

    df["GEO_CAPTION"] = [COUNTRIES[g] for g in df.GEO]
    return df


def app():

    df_all = get_eurostat_data()

    vars_and_captions = df_all[["VARIABLE", "VARIABLE_CAPTION"]].drop_duplicates()
    vars_and_captions = vars_and_captions.set_index("VARIABLE")  # .sort_index()
    vars_and_captions = vars_and_captions["VARIABLE_CAPTION"].to_dict()

    # Filtro di menu sugli anni
    year = st.sidebar.selectbox(
        "Year? (2019 has most data)", [2019, 2020, 2021], index=0
    )
    df_all = df_all[df_all.YEAR == year]

    countries = utils.get_eu_countries()
    df_all = df_all[df_all.GEO.isin(countries)]

    # Base per le variabili: tutte le disponibili nel dataset
    ALL_VARS = sorted(df_all["VARIABLE"].unique())

    # Tipo delle variabili: sorgente base, DSK calcolate, oppure entrambe?
    variables_type = st.sidebar.radio(
        "Select variable type:",
        ("All", "Source", "Calculated (set 2019 as year)"),
        index=1,
    )
    temp = pd.Series(ALL_VARS)
    if variables_type == "Source":
        ALL_VARS = temp[~temp.str.contains("_DSK")]
    elif variables_type == "Calculated (set 2019 as year)":
        ALL_VARS = temp[temp.str.contains("_DSK")]
    del temp

    st.sidebar.write("Breakdown types")

    ALL_BRKS = pd.Series(
        df_all["BREAKDOWN_TYPE"].unique()
    )  # TODO: rimuovere il brk Y0_15, solo pochi Paesi lo monitorano
    SEL_BRKS = []

    if st.sidebar.checkbox("Age", True):
        age_brks = st.sidebar.radio(
            "Age breakdowns:",
            (
                "Age (no overlap)",
                "Age (no overlap, more detail)",
                "Age (all breakdowns, with overlap)",
            ),
        )
        if age_brks == "Age (no overlap)":
            SEL_BRKS = SEL_BRKS + [
                "Y0_15",
                "Y16_24",
                "Y25_34",
                "Y35_44",
                "Y45_54",
                "Y55_64",
                "Y65_74",
                "Y75_MAX",
            ]
        elif age_brks == "Age (no overlap, more detail)":
            SEL_BRKS = SEL_BRKS + [
                "Y0_15",
                "Y16_19",
                "Y20_24",
                "Y25_34",
                "Y35_44",
                "Y45_54",
                "Y55_64",
                "Y65_74",
                "Y75_MAX",
            ]
        else:
            SEL_BRKS = SEL_BRKS + list(
                ALL_BRKS[
                    (ALL_BRKS.str.contains("^Y\\d+_\\d+$"))
                    | (ALL_BRKS.str.contains("MAX$"))
                ].values
            )

    if st.sidebar.checkbox("Edu", False):
        SEL_BRKS = SEL_BRKS + list(
            ALL_BRKS[ALL_BRKS.str.contains("^I\\d+_\\d+$")].values
        )
    if st.sidebar.checkbox("Age & Edu", False):
        SEL_BRKS = SEL_BRKS + list(ALL_BRKS[ALL_BRKS.str.contains("HI$")].values)
        SEL_BRKS = SEL_BRKS + list(ALL_BRKS[ALL_BRKS.str.contains("ME$")].values)
        SEL_BRKS = SEL_BRKS + list(ALL_BRKS[ALL_BRKS.str.contains("LO$")].values)
    if st.sidebar.checkbox("Labour", False):
        SEL_BRKS = SEL_BRKS + list(ALL_BRKS[(ALL_BRKS.str.contains("^Y25_64_"))])
    if st.sidebar.checkbox("Employment", False):
        SEL_BRKS = SEL_BRKS + list(ALL_BRKS[(ALL_BRKS.str.contains("^EMP"))])
    if st.sidebar.checkbox("Income", False):
        SEL_BRKS = SEL_BRKS + list(ALL_BRKS[(ALL_BRKS.str.contains("^HH"))])
    if st.sidebar.checkbox("Males", False):
        SEL_BRKS = SEL_BRKS + list(ALL_BRKS[ALL_BRKS.str.contains("^M_Y")].values)
    if st.sidebar.checkbox("Males & Edu", False):
        SEL_BRKS = SEL_BRKS + list(ALL_BRKS[ALL_BRKS.str.contains("^M_I")].values)
    if st.sidebar.checkbox("Females", False):
        SEL_BRKS = SEL_BRKS + list(ALL_BRKS[ALL_BRKS.str.contains("^F_Y")].values)
    if st.sidebar.checkbox("Females & Edu", False):
        SEL_BRKS = SEL_BRKS + list(ALL_BRKS[ALL_BRKS.str.contains("^F_I")].values)
    if st.sidebar.checkbox("Cross Border", False):
        SEL_BRKS = SEL_BRKS + list(ALL_BRKS[ALL_BRKS.str.contains("^CB")].values)
    if st.sidebar.checkbox("CC", False):
        SEL_BRKS = SEL_BRKS + list(ALL_BRKS[ALL_BRKS.str.contains("^CC")].values)
    if st.sidebar.checkbox("Mix on individuals", False):
        SEL_BRKS = SEL_BRKS + list(ALL_BRKS[(ALL_BRKS.str.contains("^IND_"))])
    if st.sidebar.checkbox("ISCO (with ICT category)", False):
        SEL_BRKS = SEL_BRKS + list(ALL_BRKS[(ALL_BRKS.str.contains("^ISCO_"))])
    if st.sidebar.checkbox("Various", False):
        SEL_BRKS = SEL_BRKS + list(
            ALL_BRKS[
                (
                    ALL_BRKS.isin(
                        [
                            "MD",
                            "MDX",
                            "RETIR",
                            "RETIR_OTHER",
                            "RF_GE1",
                            "RF_GE2",
                            "SAL",
                            "SAL_SELF_FAM",
                            "SELF_FAM",
                            "STUD",
                            "UNE",
                        ]
                    )
                )
            ]
        )

    df_all = df_all[df_all["BREAKDOWN_TYPE"].isin(SEL_BRKS)]

    # ---- STREAMLIT MAIN PAGE START
    st.title("Digital skills")
    st.header("Countries comparison tool")
    st.write(
        "Source data link: https://ec.europa.eu/eurostat/web/digital-economy-and-society/data/comprehensive-database"
    )
    st.write("Statistics on Households/Individuals, db version 25 March 2022")
    st.write(
        "Web app source code link: https://github.com/teamdigitale/eurostat-isoc-dashboard/blob/main/pages/digital_skills_boxplots.py"
    )

    with st.expander("Selected variables with descriptions", False):
        st.table(
            df_all[["VARIABLE", "VARIABLE_CAPTION"]]
            .drop_duplicates()
            .set_index("VARIABLE")
            .sort_index()
        )

    with st.expander("Selected breakdowns with descriptions", False):
        st.table(
            df_all[["BREAKDOWN_TYPE", "BREAKDOWN_CAPTION"]]
            .drop_duplicates()
            .set_index("BREAKDOWN_TYPE")
            .sort_index()
        )

    # --------------------------------------------------------------------------------

    if len(df_all) == 0:
        st.markdown("WARNING: filter resulted in **NO DATA**.")
        st.write()
        return

    for var in ALL_VARS:
        try:
            st.subheader(f"{vars_and_captions[var]} [{var}]")
            # st.caption(f'{vars_and_captions[var]}')
            fig = create_boxplot(df_all, var)
            fig = fig.update_xaxes(
                categoryorder="array", categoryarray=sorted(SEL_BRKS)
            )
            utils.st_create_download_btn(
                fig, "Download chart below", f"boxplot_{var}.html"
            )
            st.plotly_chart(fig, use_container_width=True)

        except:
            print(f"Problems with variable {var}")

    print("Eurostat DSK boxplots navigation page loaded.")


# %% Exec with file
if __name__ == "__main__":
    print("Eurostat data navigation app, executed as main")
    st.set_page_config(layout="wide")
    app()
