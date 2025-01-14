import streamlit as st
# from streamlit_option_menu import option_menu

# selected = option_menu(
#     menu_title="Menu",  # required
#     options=["Estimator", "Optimiser", "Other"],  # required
#     icons=["calculator", "wrench-adjustable", "x-circle"],  # optional
#     menu_icon="clouds",  # optional
#     default_index=0,  # optional
#     orientation="horizontal",
#     styles={
#         "container": {"padding": "0!important", "background-color": "#fafafa"},
#         "icon": {"color": "purple", "font-size": "25px"},
#         "nav-link": {
#             "font-size": "25px",
#             "text-align": "left",
#             "margin": "0px",
#             "--hover-color": "#eee",
#         },
#         "nav-link-selected": {"background-color": "blue"},
#     },
#     )

def menu():
    # Show a navigation menu
    st.sidebar.page_link("app.py", label="Cost Estimator")
    st.sidebar.page_link("pages/optimiser.py", label="Cloud Architecture Optimiser")
