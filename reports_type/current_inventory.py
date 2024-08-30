import streamlit as st
from streamlit_extras.stylable_container import stylable_container
from visualizations import current_inventory_viz
from side_func import get_csv_columns




def report_func(df):
    
    columns = get_csv_columns(df)
    current_inventory_viz.preprocess_data(df)
    if "Available cases (QTY)" in columns and "Wholesale price" in columns and "Category name" in columns:
        
        with st.container(border=True):
            col11, col12 = st.columns([10, 0.50])
            with col11:
                st.markdown("""
                <style>
                .big-font {
                    font-size:20px !important;
                }</style>""", unsafe_allow_html=True)
                st.markdown('<p class="big-font">Inventory Value Distribution by Category</p>', unsafe_allow_html=True)
            with col12:
                if st.button("🛈", key=444, help="Get some plot information", use_container_width=False):
                    #if render_circle_button(22):
                    condition = True
                else:
                    condition = False
                # Check the state of the button
            if condition == True:
                st.markdown("""   
                This bar chart illustrates the proportional distribution of inventory value across different product categories, allowing you to quickly see which categories hold the most significant value within your inventory.
                """)
            current_inventory_viz.df_analyze_inventory_value_by_category(df)
    else:
        st.warning("There is no Available cases (QTY) or Wholesale price columns, so visualizing can not be ready")
    
    if "Available cases (QTY)" in columns and "Retail price" in columns and "Category name" in columns and "Wholesale price" in columns:
        with st.container(border=True):
            col11, col12 = st.columns([10, 0.50])#([1, 1.705])
            with col11:
                st.markdown("""
                <style>
                .big-font {
                    font-size:20px !important;
                }</style>""", unsafe_allow_html=True)
                st.markdown('<p class="big-font">Quantity, Price, and Category: A Multi-Factor View</p>', unsafe_allow_html=True)
            with col12:
                if st.button("🛈", key=445, help="Get some plot information", use_container_width=False):
                #if render_circle_button(23):
                    condition = True
                else:
                    condition = False
                    
            if condition==True:
                st.markdown("""
                This scatter plot provides a visual analysis of the interplay between available quantity, retail price, category, and wholesale price. Explore how these factors relate to each other, uncover potential trends within categories, and identify outliers that might require further investigation. Use these insights to inform your pricing, inventory, and product strategies. 
                """)
            current_inventory_viz.df_analyze_quantity_vs_retail_price(df)
            
    else:
        st.warning("There is no Available cases (QTY) or Retail price or Category name columns, so visualizing can not be ready")
    
    if "Available cases (QTY)" in columns and "Wholesale price" in columns and "Manufacturer name" in columns:
        with st.container(border=True):
            col11, col12 = st.columns([10, 0.50])#([1, 1.95])
            with col11:
                st.markdown("""
                <style>
                .big-font {
                    font-size:20px !important;
                }</style>""", unsafe_allow_html=True)
                st.markdown('<p class="big-font">Inventory Value Distribution by Manufacturer</p>', unsafe_allow_html=True)
            with col12:
                if st.button("🛈", key=446, help="Get some plot information", use_container_width=False):
                    condition = True
                else:
                    condition = False
            if condition==True:
                st.markdown("""
                This bar chart illustrates the proportional distribution of inventory value across different manufacturers. This allows you to see at a glance which manufacturers contribute the most to your overall inventory value. 
                """)
            current_inventory_viz.df_analyze_inventory_value_by_manufacturer(df)
        
        
    else:
        st.warning("There is no Available cases (QTY) or Manufacturer name or Wholesale price columns, so visualizing can not be ready")
    
    #wih cc2:
    if "Wholesale price" in columns and "Available cases (QTY)" in columns and "Product name" in columns:
        with st.container(border=True):
            col11, col12 = st.columns([10, 0.50])#([1, 2.35])
            with col11:
                st.markdown("""
                <style>
                .big-font {
                    font-size:20px !important;
                }</style>""", unsafe_allow_html=True)
                st.markdown('<p class="big-font">Inventory Value Distribution by Product</p>', unsafe_allow_html=True)
            with col12:
                if st.button("🛈", key=447, help="Get some plot information", use_container_width=False):
                    condition = True
                else:
                    condition = False
            if condition==True:
                st.markdown("""
                This bar chart breaks down the distribution of inventory value across individual products, providing insights into which products contribute the most to the overall inventory value.
                """)
            current_inventory_viz.df_analyze_inventory_value_per_unit(df)
    else:
        st.warning("There is no Product name or Available cases (QTY) or Wholesale price columns, so visualizing can not be ready")
    
    if "Retail price" in columns and "Category name" in columns:
        with st.container(border=True):
            col11, col12 = st.columns([10, 0.50])#([1, 2])
            with col11:
                st.markdown("""
                <style>
                .big-font {
                    font-size:20px !important;
                }</style>""", unsafe_allow_html=True)
                st.markdown('<p class="big-font">Average Retail Price Distribution by Category</p>', unsafe_allow_html=True)
            with col12:
                if st.button("🛈", key=448, help="Get some plot information", use_container_width=False):
                    condition = True
                else:
                    condition = False
            if condition==True:
                st.markdown("""
                    This donut chart provides a visual representation of how average retail prices are distributed across different product categories. Easily compare the proportions and identify categories with higher or lower average prices. 
                    """)
            current_inventory_viz.df_compare_average_retail_prices(df)
    else:
        st.warning("There is no Category name or Retail price columns, so visualizing can not be ready")
        