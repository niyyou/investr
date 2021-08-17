import numpy as np
import pandas as pd
import streamlit as st

from views.register import declare_view
from box import Box


def make_sidebar(sidebar):

    with st.sidebar.expander("Inputs", True):
        sidebar.annual_gain = st.number_input(
            "annual gain (%)", min_value=0, max_value=100, value=7
        )
        sidebar.monthly_invest = st.number_input(
            "monthly investments (€)", 0, 2000, 500, 100
        )

        sidebar.starting_value = st.number_input("Starting value", min_value=0, value=0)
        sidebar.yearly_etra = st.number_input("Yearly extra", min_value=0, value=0)
        sidebar.n_years = int(
            st.number_input("Years of investment", min_value=1, value=20, step=1)
        )

    return sidebar


@declare_view("Value growth")
def show_regular(*args, **kwargs):
    sidebar = Box()
    sidebar = make_sidebar(sidebar)

    annual_invest = sidebar.monthly_invest * 12
    rate = sidebar.annual_gain / 100.0 + 1
    start_year = 2021
    n_years = sidebar.n_years

    data = []
    current_networth = sidebar.starting_value
    invested = float(sidebar.starting_value)

    data.append([start_year - 1, current_networth, invested])
    for year in range(start_year, start_year + n_years):
        current_networth = (
            current_networth + annual_invest
        ) * rate + sidebar.yearly_etra

        current_networth = round(current_networth, 0)

        invested += annual_invest + sidebar.yearly_etra
        data.append([year, current_networth, invested])

    df = pd.DataFrame(data, columns=["year", "networth", "invested"]).set_index("year")

    df["gain"] = df.networth - df.invested

    # st.dataframe(df)

    st.markdown(
        f"Networth after {n_years} years is **{round(current_networth):,} €**, with **{round(invested):,}** € invested."
    )
    st.bar_chart(df[["invested", "gain"]])

    st.dataframe(df, width=1500)
