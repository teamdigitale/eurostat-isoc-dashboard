# import numpy as np
# import pandas as pd
# import pickle
import streamlit as st
import io


# REF (8/4/22): https://ec.europa.eu/eurostat/statistics-explained/index.php?title=Glossary:Country_codes
def get_eu_countries(
    eu_union: bool = True, eu_candidates: bool = False, eu_other: bool = False
) -> dict[str, str]:
    dct_countries = dict()

    # Union (27 countries)
    if eu_union:
        dct_countries = dct_countries | {
            "AT": "Austria",
            "BE": "Belgium",
            "BG": "Bulgaria",
            "HR": "Croatia",
            "CY": "Cyprus",
            "CZ": "Czechia",
            "DK": "Denmark",
            "EE": "Estonia",
            "FI": "Finland",
            "FR": "France",
            "DE": "Germany",
            "EL": "Greece",
            "HU": "Hungary",
            "IE": "Ireland",
            "IT": "Italy",  ###
            "LV": "Latvia",
            "LT": "Lithuania",
            "LU": "Luxembourg",
            "MT": "Malta",
            "NL": "Netherlands",
            "PL": "Poland",
            "RO": "Portugal",
            "RO": "Romania",
            "SK": "Slovakia",
            "SI": "Slovenia",
            "ES": "Spain",
            "SE": "Sweden",
        }

    # Candidate countries
    if eu_candidates:
        dct_countries = dct_countries | {
            "ME": "Montenegro (EU candidate)",
            "MK": "North Macedonia (EU candidate)",
            "AL": "Albania (EU candidate)",
            "RS": "Serbia (EU candidate)",
            "TR": "Turkey (EU candidate)",
        }

    # Other
    if eu_other:
        dct_countries = dct_countries | {"UK": "United Kingdom"}

    return dct_countries


def st_create_download_btn(fig, btn_txt, html_name):
    buffer = io.StringIO()
    fig.write_html(buffer, include_plotlyjs="cdn")
    html_bytes = buffer.getvalue().encode()
    st.download_button(
        label=btn_txt, data=html_bytes, file_name=html_name, mime="text/html"
    )


def st_create_download_btn_w_parent(parent, fig, btn_txt, html_name):
    with io.StringIO() as buffer:
        fig.write_html(buffer, include_plotlyjs="cdn")
        html_bytes = buffer.getvalue().encode()
        parent.download_button(
            label=btn_txt, data=html_bytes, file_name=html_name, mime="text/html"
        )
