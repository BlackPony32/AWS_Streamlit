import streamlit as st
from streamlit_extras.stylable_container import stylable_container
from visualizations import product_fulfillment_viz
from side_func import get_csv_columns



def report_func(df):
    #st.success("This report is new, so visualizations are not available yet")
    columns = get_csv_columns(df)

    product_fulfillment_viz.preprocess_data(df)
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
    
    if True:
        try:
            with st.container(border=True):
                col11, col12 = st.columns([10, 0.50])
                with col11:
                    st.markdown("""
                    <style>
                    .big-font {
                        font-size:20px !important;
                    }</style>""", unsafe_allow_html=True)
                    st.markdown('<p class="big-font">Quantity Delivered and Returned per Sales Representative</p>', unsafe_allow_html=True)
                with col12:
                    if st.button("🛈", key=465, help="Get some plot information", use_container_width=False):
                        #if render_circle_button(22):
                        condition = True
                    else:
                        condition = False
                    # Check the state of the button
                if condition == True:
                    st.markdown("""
                        Grouped bar chart with two bars per sales representative—one for delivered quantities and one for returned quantities. 
                        It provides insight into sales rep activity, highlighting potential issues with high return rates.
                        """)
                product_fulfillment_viz.Quantity_Delivered_Returned_Per_Rep_Visualization(df)
        except Exception as e:
            print("Error in Sales_Performance_Visualization:", e)
            st.success("This visualization is temporarily unavailable")    
    else:
        #print(e)
        st.warning("There is some error with plot, so visualizing can not be ready")
        
        
 
    if True:
        try:
            with st.container(border=True):
                col11, col12 = st.columns([10, 0.50])
                with col11:
                    st.markdown("""
                    <style>
                    .big-font {
                        font-size:20px !important;
                    }</style>""", unsafe_allow_html=True)
                    st.markdown('<p class="big-font">Total Quantity Sold Over Time</p>', unsafe_allow_html=True)
                with col12:
                    if st.button("🛈", key=466, help="Get some plot information", use_container_width=False):
                        #if render_circle_button(22):
                        condition = True
                    else:
                        condition = False
                    # Check the state of the button
                if condition == True:
                    st.markdown("""
                    This visualization is a line chart showing the total quantity of products sold (delivered) over time,
                    aggregated by month. It tracks sales performance trends, helping businesses identify seasonal patterns or growth
                    opportunities.
                    """)
                product_fulfillment_viz.Quantity_Sold_Over_Time_Visualization(df)
        except Exception as e:
            print("Error in Quantity_Sold_Over_Time_Visualization:", e)
            st.success("This visualization is temporarily unavailable")
    else:
        #print(e)
        st.warning("There is some error with plot, so visualizing can not be ready")