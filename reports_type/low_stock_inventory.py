import streamlit as st
from streamlit_extras.stylable_container import stylable_container
from visualizations import low_stock_inventory_viz
from side_func import get_csv_columns




def report_func(df):
    
    columns = get_csv_columns(df)
    low_stock_inventory_viz.preprocess_data(df)
    
    if "Category name" in columns and "Product name" in columns and "Available cases (QTY)" in columns and "Wholesale price" in columns:
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
                if st.button("🛈", key=490, help="Get some plot information", use_container_width=False):
                    #if render_circle_button(22):
                    condition = True
                else:
                    condition = False
            with stylable_container(
            key="custom-tabs1-button",
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
                    width: 200px;
                    height: 30px;
                    line-height: 30px;
                    position: relative;
                }""",
                """
                button:hover {
                    background-color: #ffffff;
                    box-shadow: 0 12px 16px 0 rgba(0,0,0,0.24), 0 17px 50px 0 rgba(0,0,0,0.19);
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
                tab1, tab2 = st.tabs(["Distribution by Category", "Price vs. Quantity"])
                with tab1:
                    if condition == True:
                        st.markdown("""
                        This analysis focuses on products with low stock levels. The first chart breaks down these items by category, allowing you to quickly pinpoint areas of concern. The second chart visualizes the relationship between wholesale price and available quantity, offering a more granular perspective on inventory levels for each product.  
                        """)
                    low_stock_inventory_viz.low_stock_analysis_app1(df)
                with tab2:
                    if condition == True:
                        st.markdown("""
                        This analysis focuses on products with low stock levels. The first chart breaks down these items by category, allowing you to quickly pinpoint areas of concern. The second chart visualizes the relationship between wholesale price and available quantity, offering a more granular perspective on inventory levels for each product.  
                        """)
                    low_stock_inventory_viz.low_stock_analysis_app2(df)
    else:
        st.warning("There is no Available cases (QTY) or Category name or Product name columns, so visualizing can not be ready")
    
    if "Retail price" in columns and "Wholesale price" in columns and "Product name" in columns:
        with st.container(border=True):
            col11, col12 = st.columns([10, 0.45])
            with col11:
                st.markdown("""
                <style>
                .big-font {
                    font-size:20px !important;
                }</style>""", unsafe_allow_html=True)
                st.markdown('<p class="big-font">Profit Margins: Low Stock Items</p>', unsafe_allow_html=True)
            with col12:
                if st.button("🛈", key=491, help="Get some plot information", use_container_width=False):
                    #if render_circle_button(22):
                    condition = True
                else:
                    condition = False
                # Check the state of the button
            if condition == True:
                st.markdown("""
                This bar chart highlights the profit margins of your low-stock items, sorted from highest to lowest. Prioritize replenishing high-margin products to maximize potential revenue and avoid stockouts.  
                """)
            low_stock_inventory_viz.create_profit_margin_analysis_plot(df)
    else:
        st.warning("There is no Product name or Retail price or Wholesale price columns, so visualizing can not be ready")
    
    if "Manufacturer name" in columns and "Product name" in columns:
        with st.container(border=True):
            col11, col12 = st.columns([10, 0.45])
            with col11:
                st.markdown("""
                <style>
                .big-font {
                    font-size:20px !important;
                }</style>""", unsafe_allow_html=True)
                st.markdown('<p class="big-font">Low Stock Items by Manufacturer</p>', unsafe_allow_html=True)
            with col12:
                if st.button("🛈", key=492, help="Get some plot information", use_container_width=False):
                    #if render_circle_button(22):
                    condition = True
                else:
                    condition = False
                # Check the state of the button
            if condition == True:
                st.markdown("""
                This bar chart highlights the manufacturers with the highest number of low-stock items, providing insights into potential supplier-related challenges or product popularity. By analyzing this breakdown, you can proactively address inventory concerns and strengthen your supply chain relationships.  
                """)
            low_stock_inventory_viz.create_low_stock_by_manufacturer_bar_plot(df)
    else:
        st.warning("There is no Manufacturer name or Product name columns, so visualizing can not be ready")
    
    #wih cc2:
    if "Wholesale price" in columns and "Available cases (QTY)" in columns:
        with st.container(border=True):
            col11, col12 = st.columns([10, 0.45])
            with col11:
                st.markdown("""
                <style>
                .big-font {
                    font-size:20px !important;
                }</style>""", unsafe_allow_html=True)
                st.markdown('<p class="big-font">Price vs. Quantity: Low-Stock Items</p>', unsafe_allow_html=True)
            with col12:
                if st.button("🛈", key=493, help="Get some plot information", use_container_width=False):
                    #if render_circle_button(22):
                    condition = True
                else:
                    condition = False
                # Check the state of the button
            if condition == True:
                st.markdown("""
                This scatter plot explores the relationship between wholesale price and available quantity for products currently low in stock. The trendline helps you visualize the general association between these factors. Analyze this visualization to inform your inventory management decisions and potentially predict future stock requirements.
                """)
            low_stock_inventory_viz.create_interactive_price_vs_quantity_plot(df)
    else:
        st.warning("There is no Available cases (QTY) or Wholesale price columns, so visualizing can not be ready")
    
    if "Retail price" in columns and "Available cases (QTY)" in columns and "Product name" in columns:
        with st.container(border=True):
            col11, col12 = st.columns([10, 0.45])
            with col11:
                st.markdown("""
                <style>
                .big-font {
                    font-size:20px !important;
                }</style>""", unsafe_allow_html=True)
                st.markdown('<p class="big-font">Quantity/Price Ratio: Low-Stock Items</p>', unsafe_allow_html=True)
            with col12:
                if st.button("🛈", key=494, help="Get some plot information", use_container_width=False):
                    #if render_circle_button(22):
                    condition = True
                else:
                    condition = False
                # Check the state of the button
            if condition == True:
                st.markdown("""
                This horizontal bar chart visualizes the ratio of available quantity to retail price for each low-stock item. Products with higher ratios might indicate overstocking or potential pricing issues, while those with lower ratios could signal high demand or potential stock shortages.
                """)
            low_stock_inventory_viz.create_quantity_price_ratio_plot(df)
    else:
        st.warning("There is no Available cases (QTY) or Retail price columns, so visualizing can not be ready")
        