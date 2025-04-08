import streamlit as st
from streamlit_extras.stylable_container import stylable_container
from visualizations import inventory_depletion_viz
from side_func import get_csv_columns



def report_func(df):
    #st.success("This report is new, so visualizations are not available yet")
    columns = get_csv_columns(df)

    inventory_depletion_viz.preprocess_data(df)
    css='''
<style>

    .stTabs [data-baseweb="tab-highlight"] {
        background-color: #409A65;
    }
    .stTabs [data-baseweb="tab-border"] {
        width: 102.8%;
        left: -16px; 
    }
    
}
</style>
'''
    st.markdown(css, unsafe_allow_html=True)
    #st.write(columns)
    try:
    #if "Date" in columns and "Role" in columns and "Total revenue" in columns:
        with st.container(border=True):
            col11, col12 = st.columns([10, 0.50])
            with col11:
                st.markdown("""
                <style>
                .big-font {
                    font-size:20px !important;
                }</style>""", unsafe_allow_html=True)
                st.markdown('<p class="big-font">Top 12 Inventory Depletion by Business</p>', unsafe_allow_html=True)
            with col12:
                if st.button("🛈", key=465, help="Get some plot information", use_container_width=False):
                    #if render_circle_button(22):
                    condition = True
                else:
                    condition = False
                # Check the state of the button
            if condition == True:
                st.markdown("""
This bar chart visualizes the top 12 products with the highest depletion quantities across different businesses. 
The stacked bars represent the contribution of each product to the total inventory depletion for each business. 
Use this chart to identify trends in product demand, pinpoint high-demand items, and assess inventory performance 
across various locations.
""")
            inventory_depletion_viz.Inventory_Depletion_Visualization(df)
    except Exception as e:
        print(e)
        st.success("This visualization is temporarily unavailable")