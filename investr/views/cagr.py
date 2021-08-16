import streamlit as st
from streamlit.caching import CachedStFunctionWarning
from views.register import declare_view
import numpy as np
from box import Box


def make_sidebar(params):

    with st.sidebar.expander("Inputs", True):
        params.starting_value = st.number_input(
            "starting value",
            value=1000,
            min_value=1,
        )
        params.ending_value = st.number_input(
            "ending value", value=1000000, min_value=1
        )
        params.n_years = st.number_input(
            "number of years", value=20, max_value=100, min_value=1
        )
    return params


@declare_view("CAGR")
def show_cagr(*args, **kwargs):
    sidebar = Box()
    sidebar = make_sidebar(sidebar)

    cagr = (sidebar.ending_value / sidebar.starting_value) ** (1 / sidebar.n_years) - 1

    st.write("CAGR", cagr)
