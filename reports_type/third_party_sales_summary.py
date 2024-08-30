import streamlit as st
from streamlit_extras.stylable_container import stylable_container
from visualizations import third_party_sales_viz
from side_func import get_csv_columns


def report_func(df):

    columns = get_csv_columns(df)
    third_party_sales_viz.preprocess_data(df)
    if "Product name" in columns and "Grand total" in columns:
        with st.container(border=True):
            col11, col12 = st.columns([10, 0.50])
            with col11:
                st.markdown("""
                <style>
                .big-font {
                    font-size:20px;
                }</style>""", unsafe_allow_html=True)
                st.markdown('<p class="big-font">Inventory Total Revenue by Product</p>', unsafe_allow_html=True)
            with col12:
                if st.button("🛈", key=424, help="Get some plot information", use_container_width=False):
                    #if render_circle_button(22):
                    condition = True
                else:
                    condition = False
                # Check the state of the button
            with stylable_container(
            key="custom-tabs-button",
            css_styles=["""
                button {
                    background-color: #ffffff;
                    border: 2px solid #ffffff;
                    color: #5f6267;
                    padding: 0px;
                    text-align: center;
                    text-decoration: none;
                    border-radius: 0%;
                    font-size: 19px;
                    margin: 4px 2px;
                    border-style: solid;
                    width: 110px;
                    height: 30px;
                    line-height: 30px;
                    position: relative;
                }""",
                """
                button:hover {
                    background-color: #ffffff;
                    color: #409A65;
                }""",
                """
                button:focus {
                    background-color: #ffffff;
                    color: #409A65;
                    border: 2px #ffffff;
                }
                """],
            ):
                tab1, tab2 = st.tabs(["Total Sales", "Order Distribution"])
                with tab1:
                    if condition == True:
                        st.markdown("""
                        This chart shows how total sales are split across product categories over time. See which categories drive sales in each period and spot any trends.
                        """)
                    third_party_sales_viz.visualize_product_analysis1(df)
                with tab2:
                    if condition == True:
                        st.markdown("""
                        This chart displays the number of orders for each product, indicating their popularity and helping you manage inventory effectively.
                        """)
                    third_party_sales_viz.visualize_product_analysis2(df)
                
    else:
        st.warning("There is no Grand total or Product name, so visualizing can not be ready")
    
    if "Customer" in columns and "Product name" in columns and "QTY" in columns and "Grand total" in columns:
        with st.container(border=True):
            col11, col12 = st.columns([10, 0.50])
            with col11:
                st.markdown("""
                <style>
                .big-font {
                    font-size:20px ;
                }</style>""", unsafe_allow_html=True)
                st.markdown('<p class="big-font">Top 10 Customers by Sales Amount</p>', unsafe_allow_html=True)
            with col12:
                if st.button("🛈", key=425, help="Get some plot information", use_container_width=False):
                    #if render_circle_button(22):
                    condition = True
                else:
                    condition = False
                # Check the state of the button
            if condition == True:
                st.markdown("""
            This chart highlights your top 10 customers by sales revenue. Prioritize these key relationships to drive future sales and consider loyalty programs to encourage repeat business.
            """)
            third_party_sales_viz.visualize_sales_trends(df)
    else:
        st.warning("There is no Customer or Product name or Quantity or Grand total, so visualizing can not be ready")
    
    if "Product name" in columns and "QTY" in columns and "Grand total" in columns:
        with st.container(border=True):
            col11, col12 = st.columns([10, 0.50])
            with col11:
                st.markdown("""
                <style>
                .big-font {
                    font-size:20px;
                }</style>""", unsafe_allow_html=True)
                st.markdown('<p class="big-font">Dependence between Quantity and Amount (by Product)</p>', unsafe_allow_html=True)
            with col12:
                if st.button("🛈", key=426, help="Get some plot information", use_container_width=False):
                    #if render_circle_button(22):
                    condition = True
                else:
                    condition = False
                # Check the state of the button
            if condition == True:
                st.markdown("""
                This chart shows how sales revenue varies with the quantity of products sold, broken down by product name. Analyze which products contribute the most at different quantity levels.
                """)
            third_party_sales_viz.visualize_combined_analysis(df)
    else:
        st.warning("There is no Delivery status or Product name or Quantity or Grand total, so visualizing can not be ready")
    
    if "Discount type" in columns:
        with st.container(border=True):
            col11, col12 = st.columns([10, 0.50])
            with col11:
                st.markdown("""
                <style>
                .big-font {
                    font-size:20px !important;
                }</style>""", unsafe_allow_html=True)
                st.markdown('<p class="big-font">Dependence between Quantity and Amount (by Product)</p>', unsafe_allow_html=True)
            with col12:
                if st.button("🛈", key=427, help="Distribution of Discount Types", use_container_width=False):
                    #if render_circle_button(22):
                    condition = True
                else:
                    condition = False
                # Check the state of the button
            if condition == True:
                st.markdown("""
            This chart presents the distribution of discount types used in orders. It highlights the proportion of orders associated with each discount category.
            """)
            third_party_sales_viz.analyze_discounts(df)
    else:
        st.warning("There is no Discount type, so visualizing can not be ready")
    if "Grand total" in columns and "Manufacturer specific discount" in columns and "Customer discount" in columns:
        with st.container(border=True):
            col11, col12 = st.columns([10, 0.50])
            with col11:
                st.markdown("""
                <style>
                .big-font {
                    font-size:20px !important;
                }</style>""", unsafe_allow_html=True)
                st.markdown('<p class="big-font">Dependence between Quantity and Amount (by Product)</p>', unsafe_allow_html=True)
            with col12:
                if st.button("🛈", key=428, help="Sales, Manufacturer, and Customer Discounts Over Time", use_container_width=False):
                    #if render_circle_button(22):
                    condition = True
                else:
                    condition = False
                # Check the state of the button
            if condition == True:
                st.markdown("""
            This area chart displays how the grand total, manufacturer discounts, and customer discounts have fluctuated over time. Track how these values change, identifying periods of high discounts and understanding the overall impact of discounts on sales revenue. 
            """)
            third_party_sales_viz.area_visualisation(df)
    else:
        st.warning("There is no Grand total or Manufacturer specific discount or Customer discount, so visualizing can not be ready")
    