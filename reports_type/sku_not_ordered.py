import streamlit as st
from streamlit_extras.stylable_container import stylable_container
from visualizations import skus_not_ordered_viz
from side_func import get_csv_columns




def report_func(df):
    
    columns = get_csv_columns(df)
    skus_not_ordered_viz.preprocess_data(df)
    
    if "Category Name" in columns:
        try:
            with st.container(border=True):
                col11, col12 = st.columns([10, 0.50])
                with col11:
                    st.markdown("""
                    <style>
                    .big-font {
                        font-size:20px !important;
                    }</style>""", unsafe_allow_html=True)
                    st.markdown('<p class="big-font">Unordered Products: A Category-Based View</p>', unsafe_allow_html=True)
                with col12:
                    if st.button("🛈", key=472, help="Get some plot information", use_container_width=False):
                        #if render_circle_button(22):
                        condition = True
                    else:
                        condition = False
                    # Check the state of the button
                if condition == True:
                    st.markdown("""
                This bar chart displays the number of unordered products in each category. Use this visualization to identify potential stock shortages, prioritize reordering, and refine your inventory management strategies.
                """)
                skus_not_ordered_viz.create_unordered_products_by_category_plot(df)
        except Exception as e:
            print("Error in create_unordered_products_by_category_plot:", e)
            st.success("This visualization is temporarily unavailable")
    else:
        st.warning("There is no Category Name column, so visualizing can not be ready")
    
    if "Available Cases (QTY)" in columns:
        try:
            with st.container(border=True):
                col11, col12 = st.columns([10, 0.50])
                with col11:
                    st.markdown("""
                    <style>
                    .big-font {
                        font-size:20px !important;
                    }</style>""", unsafe_allow_html=True)
                    st.markdown('<p class="big-font">Distribution of Products by Stock Level</p>', unsafe_allow_html=True)
                with col12:
                    if st.button("🛈", key=473, help="Get some plot information", use_container_width=False):
                        #if render_circle_button(22):
                        condition = True
                    else:
                        condition = False
                    # Check the state of the button
                if condition == True:
                    st.markdown("""
                    This donut chart presents a clear picture of how your products are distributed across different stock levels. It provides a quick assessment of potential stock shortages ("Low Stock"), healthy inventory levels ("Medium Stock"), and potential overstocking ("High Stock"). 
                    """)
                skus_not_ordered_viz.create_available_cases_distribution_plot(df)
        except Exception as e:
            print("Error in create_available_cases_distribution_plot:", e)
            st.success("This visualization is temporarily unavailable")
    else:
        st.warning("There is no Available cases (QTY) column, so visualizing can not be ready")
    
    if "Category Name" in columns and "Retail Price" in columns and "Available Cases (QTY)" in columns:
        try:
            with st.container(border=True):
                col11, col12 = st.columns([10, 0.50])
                with col11:
                    st.markdown("""
                    <style>
                    .big-font {
                        font-size:20px !important;
                    }</style>""", unsafe_allow_html=True)
                    st.markdown('<p class="big-font">Distribution of Products by Stock Level</p>', unsafe_allow_html=True)
                with col12:
                    if st.button("🛈", key=474, help="Get some plot information", use_container_width=False):
                        #if render_circle_button(22):
                        condition = True
                    else:
                        condition = False
                    # Check the state of the button
                if condition == True:
                    st.markdown("""
                    This bar chart displays the average available cases for the selected product category across different retail price ranges. Use this information to identify potential stock imbalances within price ranges and make informed decisions about inventory management and pricing strategies. 
                    """)
                skus_not_ordered_viz.price_vs_available_cases_app(df)
        except Exception as e:
            print("Error in price_vs_available_cases_app:", e)
            st.success("This visualization is temporarily unavailable")
    else:
        st.warning("There is no Category Name or Retail Price or Available Cases (QTY) columns, so visualizing can not be ready")
    
    #wih cc2:
    if "Available Cases (QTY)" in columns and "Retail Price" in columns and "Wholesale Price" in columns and "Category Name" in columns:
        try:
            with st.container(border=True):
                col11, col12 = st.columns([10, 0.50])
                with col11:
                    st.markdown("""
                    <style>
                    .big-font {
                        font-size:20px !important;
                    }</style>""", unsafe_allow_html=True)
                    st.markdown('<p class="big-font">Profit & Pricing: Analyzing Relationships</p>', unsafe_allow_html=True)
                with col12:
                    if st.button("🛈", key=475, help="Get some plot information", use_container_width=False):
                        #if render_circle_button(22):
                        condition = True
                    else:
                        condition = False
                with stylable_container(
                key="custom-tabs2-button",
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
                        width: 190px;
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
                    tab1, tab2 = st.tabs(["Available Cases vs Profit Margin", "Wholesale vs Retail Price"])
                    with tab1:
                        if condition == True:
                            st.markdown("""
                        These scatter plots help you explore the connections between available cases, profit margins, wholesale prices, and retail prices. Use these visualizations to identify potential trends, outliers, and opportunities for optimizing pricing and inventory strategies. 
                        """)
                        skus_not_ordered_viz.create_wholesale_vs_retail_price_scatter1(df)
                    with tab2:
                        if condition == True:
                            st.markdown("""
                        These scatter plots help you explore the connections between available cases, profit margins, wholesale prices, and retail prices. Use these visualizations to identify potential trends, outliers, and opportunities for optimizing pricing and inventory strategies. 
                        """)
                        skus_not_ordered_viz.create_wholesale_vs_retail_price_scatter2(df)
        except Exception as e:
            print("Error in create_wholesale_vs_retail_price_scatter2:", e)
            st.success("This visualization is temporarily unavailable")
    else:
        st.warning("There is no Available Cases (QTY) or Retail Price or Wholesale Price columns, so visualizing can not be ready")

    if "Category Name" in columns and "Retail Price" in columns:
        try:
            with st.container(border=True):
                col11, col12 = st.columns([10, 0.50])
                with col11:
                    st.markdown("""
                    <style>
                    .big-font {
                        font-size:20px !important;
                    }</style>""", unsafe_allow_html=True)
                    st.markdown('<p class="big-font">Unordered Products: Category and Price View</p>', unsafe_allow_html=True)
                with col12:
                    if st.button("🛈", key=477, help="Get some plot information", use_container_width=False):
                        #if render_circle_button(22):
                        condition = True
                    else:
                        condition = False
                    # Check the state of the button
                if condition == True:
                    st.markdown("""
                    This heatmap reveals the distribution of unordered products across different categories and price ranges. Deeper colors represent a higher concentration of unordered items. Analyze this visualization to identify potential stock shortages, prioritize reordering based on price and category, and optimize inventory management strategies. 
                    """)
                skus_not_ordered_viz.df_unordered_products_per_category_and_price_range(df)
        except Exception as e:
            print("Error in df_unordered_products_per_category_and_price_range:", e)
            st.success("This visualization is temporarily unavailable")
    else:
        st.warning("There is no Category name or Retail price columns, so visualizing can not be ready")
        