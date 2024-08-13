import streamlit as st
from streamlit_extras.stylable_container import stylable_container
from visualizations import top_customers_viz
from side_func import get_csv_columns




def report_func(df):
    
    columns = get_csv_columns(df)
    top_customers_viz.preprocess_data(df)
    if "Name" in columns and "Total sales" in columns and "Territory" in columns and "Payment terms" in columns:
        with st.container(border=True):
            col11, col12 = st.columns([10, 0.45])
            with col11:
                st.markdown("""
                <style>
                .big-font {
                    font-size:20px !important;
                }</style>""", unsafe_allow_html=True)
                st.markdown('<p class="big-font">Low Stock Inventory Analysis</p>', unsafe_allow_html=True)
            with col12:
                if st.button("🛈", key=505, help="Customer Sales Analysis", use_container_width=False):
                    #if render_circle_button(22):
                    condition = True
                else:
                    condition = False
            with stylable_container(
            key="custom-tabs1-button",
            css_styles=["""
                button {
                    background-color: #ffffff;
                    border: 2px solid #47A06D;
                    color: #47A06D;
                    padding: 0px;
                    text-align: center;
                    text-decoration: none;
                    
                    font-size: 17px;
                    margin: 4px 2px;
                    border-style: solid;
                    width: 150px;
                    height: 30px;
                    line-height: 30px;
                    position: relative;
                }""",
                """
                button:hover {
                    background-color: #409A65;
                    box-shadow: 0 12px 16px 0 rgba(0,0,0,0.24), 0 17px 50px 0 rgba(0,0,0,0.19);
                    color: #ffffff;
                }""",
                """
                button:focus {
                    background-color: #409A65;
                    color: #ffffff;
                    border: 2px #47A06D;
                }
                """],
            ):
                tab1, tab2, tab3 = st.tabs(["Top Customers", "Territory Analysis", "Payment Terms Analysis"])
                with tab1:
                    if condition == True:
                        st.markdown("""
                        This dashboard provides an overview of customer sales patterns, focusing on your top-performing customers, sales distribution across different territories, and a breakdown of sales by payment terms. Use this information to identify key customer segments, optimize sales strategies, and improve cash flow management.
                        """)
                    top_customers_viz.customer_analysis_app1(df)
                with tab2:
                    if condition == True:
                        st.markdown("""
                        This dashboard provides an overview of customer sales patterns, focusing on your top-performing customers, sales distribution across different territories, and a breakdown of sales by payment terms. Use this information to identify key customer segments, optimize sales strategies, and improve cash flow management.
                        """)
                    top_customers_viz.customer_analysis_app2(df)
                with tab3:
                    if condition == True:
                        st.markdown("""
                        This dashboard provides an overview of customer sales patterns, focusing on your top-performing customers, sales distribution across different territories, and a breakdown of sales by payment terms. Use this information to identify key customer segments, optimize sales strategies, and improve cash flow management.
                        """)
                    top_customers_viz.customer_analysis_app3(df)
    else:
        st.warning("There is no Name or Total sales or Territory or Payment terms columns, so visualizing can not be ready")
    
    if "Payment terms" in columns:
        with st.container(border=True):
            col11, col12 = st.columns([10, 0.45])
            with col11:
                st.markdown("""
                <style>
                .big-font {
                    font-size:20px !important;
                }</style>""", unsafe_allow_html=True)
                st.markdown('<p class="big-font">Distribution by every columns</p>', unsafe_allow_html=True)
            with col12:
                if st.button("🛈", key=506, help="Get some plot information", use_container_width=False):
                    #if render_circle_button(22):
                    condition = True
                else:
                    condition = False
                # Check the state of the button
            if condition == True:
                st.markdown("""Useful to see data distribution of all columns
                """)
            top_customers_viz.interactive_bar_plot_app(df)
    else:
        st.warning("There is no Payment terms column, so visualizing can not be ready")
    
    #wih cc2:
    if "Total sales" in columns:
        with st.container(border=True):
            col11, col12 = st.columns([10, 0.45])
            with col11:
                st.markdown("""
                <style>
                .big-font {
                    font-size:20px !important;
                }</style>""", unsafe_allow_html=True)
                st.markdown('<p class="big-font">Distribution of Non-Zero Total Sales</p>', unsafe_allow_html=True)
            with col12:
                if st.button("🛈", key=507, help="Get some plot information", use_container_width=False):
                    #if render_circle_button(22):
                    condition = True
                else:
                    condition = False
                # Check the state of the button
            if condition == True:
                st.markdown("""
            This line chart illustrates the distribution of non-zero total sales values, providing a visual representation of sales frequencies. Analyze the shape of the line to identify common sales value ranges, potential outliers (sudden spikes or drops), and gain a better understanding of the overall sales distribution.
            """)
            top_customers_viz.create_non_zero_sales_grouped_plot(df)
    else:
        st.warning("There is no Total sales column, so visualizing can not be ready")
    
    if "Group" in columns and "Billing city" in columns:
        with st.container(border=True):
            col11, col12 = st.columns([10, 0.45])
            with col11:
                st.markdown("""
                <style>
                .big-font {
                    font-size:20px !important;
                }</style>""", unsafe_allow_html=True)
                st.markdown('<p class="big-font">Customer Group Distribution</p>', unsafe_allow_html=True)
            with col12:
                if st.button("🛈", key=508, help="Get some plot information", use_container_width=False):
                    #if render_circle_button(22):
                    condition = True
                else:
                    condition = False
                # Check the state of the button
            if condition == True:
                st.markdown("""
            This interactive visualization explores the distribution of customer groups across different cities. Analyze how customer groups are concentrated or spread out geographically, identify key markets, and uncover potential opportunities for expansion or targeted marketing efforts. 
            """)
            with stylable_container(
            key="custom-tabs1-button",
            css_styles=["""
                button {
                    background-color: #ffffff;
                    border: 2px solid #47A06D;
                    color: #47A06D;
                    padding: 0px;
                    text-align: center;
                    text-decoration: none;
                    
                    font-size: 17px;
                    margin: 4px 2px;
                    border-style: solid;
                    width: 150px;
                    height: 30px;
                    line-height: 30px;
                    position: relative;
                }""",
                """
                button:hover {
                    background-color: #409A65;
                    box-shadow: 0 12px 16px 0 rgba(0,0,0,0.24), 0 17px 50px 0 rgba(0,0,0,0.19);
                    color: #ffffff;
                }""",
                """
                button:focus {
                    background-color: #409A65;
                    color: #ffffff;
                    border: 2px #47A06D;
                }
                """],
            ):
                top_customers_viz.interactive_group_distribution_app(df)
    else:
        st.warning("There is no Group or Billing city columns, so visualizing can not be ready")
        