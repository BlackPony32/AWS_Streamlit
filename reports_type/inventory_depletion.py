import streamlit as st
from streamlit_extras.stylable_container import stylable_container
from visualizations import customer_details_viz
from side_func import get_csv_columns



def report_func(df):
    st.success("This report is new, so visualizations are not available yet")