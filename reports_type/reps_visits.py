import streamlit as st
from streamlit_extras.stylable_container import stylable_container
from visualizations import reps_visits_viz
from side_func import get_csv_columns



def report_func(df):
    #st.success("This report is new, so visualizations are not available yet")
    columns = get_csv_columns(df)

    reps_visits_viz.preprocess_data(df)
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
    
    if "Business Name" in columns and "Cases sold (Direct)" in columns and "Cases sold (3rd party)" in columns:
        try:
            with st.container(border=True):
                col11, col12 = st.columns([10, 0.50])
                with col11:
                    st.markdown("""
                    <style>
                    .big-font {
                        font-size:20px !important;
                    }</style>""", unsafe_allow_html=True)
                    st.markdown('<p class="big-font">Direct vs. 3rd Party Sales Performance by Business</p>', unsafe_allow_html=True)
                with col12:
                    if st.button("🛈", key=465, help="Get some plot information", use_container_width=False):
                        #if render_circle_button(22):
                        condition = True
                    else:
                        condition = False
                    # Check the state of the button
                if condition == True:
                    st.markdown("""
                        This grouped bar chart compares the performance of direct sales against 3rd party sales for each business. 
                        It helps identify which sales channel performs better at different businesses and provides insights into 
                        potential areas for improvement or expansion.
                        """)
                reps_visits_viz.Sales_Performance_Visualization(df)
        except Exception as e:
            print("Error in Sales_Performance_Visualization:", e)
            st.success("This visualization is temporarily unavailable")    
    else:
        #print(e)
        st.warning("There is some error with plot, so visualizing can not be ready")
        
        
 
    if "Name" in columns and "Date" in columns and "Cases sold total" in columns:
        try:
            with st.container(border=True):
                col11, col12 = st.columns([10, 0.50])
                with col11:
                    st.markdown("""
                    <style>
                    .big-font {
                        font-size:20px !important;
                    }</style>""", unsafe_allow_html=True)
                    st.markdown('<p class="big-font">Total Cases Sold Over Time by Sales Representative</p>', unsafe_allow_html=True)
                with col12:
                    if st.button("🛈", key=466, help="Get some plot information", use_container_width=False):
                        #if render_circle_button(22):
                        condition = True
                    else:
                        condition = False
                    # Check the state of the button
                if condition == True:
                    st.markdown("""
                    This line chart visualizes the total cases sold over time by each sales representative. 
                    It helps track performance trends, identify high-performing representatives, and analyze sales activity 
                    on specific dates.
                    """)
                reps_visits_viz.Sales_Trend_Visualization(df)
        except Exception as e:
            print("Error in Sales_Trend_Visualization:", e)
            st.success("This visualization is temporarily unavailable")
    else:
        #print(e)
        st.warning("There is some error with plot, so visualizing can not be ready")