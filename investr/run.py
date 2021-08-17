import os
import streamlit as st

st.set_page_config(
    page_title="Household Investment Simulator",
    layout="wide",
    page_icon="🏠",
)


from views import register as views_register


def cli():
    os.system("streamlit run simulation/run.py")


# query params
views_names = list(views_register.keys())
default_view = views_names[0]
query_params = st.experimental_get_query_params()

default_view_index = 0
if "view" in query_params and query_params["view"][0] in views_names:
    queried_view = query_params["view"][0]
    default_view_index = views_names.index(queried_view)


selected_view = st.sidebar.selectbox(
    "Views",
    views_names,
    index=default_view_index,
)

# if selected_view:
#     st.experimental_set_query_params(view=selected_view)
# else:
#     selected_view = queried_view

views_register[selected_view]()  # common_data
