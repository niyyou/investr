import streamlit as st
from views.register import declare_view
import numpy as np
from box import Box


def make_sidebar(params):

    with st.sidebar.expander("Inputs", True):
        params.annual_gain = st.number_input("annual gain (%)", 0, 100, 7) / 100.0 + 1
    return params


@declare_view("template")
def show_template(*args, **kwargs):
    sidebar = Box()
    sidebar = make_sidebar(sidebar)

    st.write("Hollow world!")

    # datasets_path = "datasets_4b/" + "dataset_groove_validation_label_4bars.npz"

    # X = np.load(datasets_path)
    # st.write(list(X.keys()))
    # st.write(X["style_primary"])
    # st.write(np.array(X["style_secondary"], dtype=str))
    # st.write(X["_PRIMARY_STYLES"])
    # st.write(X["dataset_drum"].shape)
    # st.write(X["dataset_drum_humanization"].shape)
