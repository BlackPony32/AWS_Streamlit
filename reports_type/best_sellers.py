import streamlit as st
from streamlit_extras.stylable_container import stylable_container
from visualizations import best_sellers_viz
from side_func import get_csv_columns




def report_func(df):
        
    best_sellers_viz.preprocess_data(df)
    columns = get_csv_columns(df)
    
    if "Available cases (QTY)" in columns and "Product name" in columns:
        with st.container(border=True):
            col11, col12 = st.columns([10, 0.45])
            with col11:
                st.markdown("""
                <style>
                .big-font {
                    font-size:20px !important;
                }</style>""", unsafe_allow_html=True)
                st.markdown('<p class="big-font">Total Revenue by Product</p>', unsafe_allow_html=True)
            with col12:
                if st.button("🛈", key=434, help="Get some plot information", use_container_width=False):
                    #if render_circle_button(22):
                    condition = True
                else:
                    condition = False
                # Check the state of the button
            if condition == True:
                st.markdown("""
                This chart visualizes the available inventory for each product. Red dots indicate products with negative inventory (potential stockouts). Green dots represent products with positive inventory. Use it to:
                * **Track Inventory Trends:** Identify periods of high and low inventory, and sudden fluctuations. 
                * **Compare Product Inventory:** See differences in stock patterns across products.
                * **Spot Potential Issues:** Find products with consistently low or negative inventory, indicating potential stockouts. 
                * **Make Informed Decisions:** Guide inventory management, production planning, and sales strategies.
                """)
            best_sellers_viz.create_available_cases_plot(df)
    else:
        st.warning("There is no Product name or Available cases (QTY) columns, so visualizing can not be ready")
    
    if "Product name" in columns and "Total revenue" in columns and "Cases sold" in columns:
        with st.container(border=True):
            col11, col12 = st.columns([10, 0.45])
            with col11:
                st.markdown("""
                <style>
                .big-font {
                    font-size:20px !important;
                }</style>""", unsafe_allow_html=True)
                st.markdown('<p class="big-font">Inventory Levels of Products Over Time</p>', unsafe_allow_html=True)
            with col12:
                if st.button("🛈", key=435, help="Get some plot information", use_container_width=False):
                    #if render_circle_button(22):
                    condition = True
                else:
                    condition = False
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
                    font-size: 17px;
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
                tab1, tab2 = st.tabs(["Total Revenue", "Cases Sold"])
                with tab1:
                    if condition == True:
                        st.markdown("""
                        This chart breaks down the total revenue generated by each product, allowing for a clear comparison of their individual contributions to overall sales. Use this to:
                        * **Identify Top Performers:** Quickly see which products are driving the most revenue.
                        * **Prioritize Product Focus:** Determine which products to focus marketing and sales efforts on.
                        * **Analyze Product Performance:** Compare revenue performance over time to track growth or decline of individual products.
                        """)
                    best_sellers_viz.product_analysis_app1(df)
                with tab2:
                    if condition == True:
                        st.markdown("""
                        This visualization presents the number of cases sold for each product, providing a direct measure of their sales volume.  This allows you to:
                        * **Assess Product Popularity:**  Identify the products with the highest sales volume.
                        * **Manage Inventory:**  Track sales volumes to inform inventory management decisions and prevent stockouts of popular products.
                        * **Identify Underperforming Products:**  See which products have low sales volumes and might require further analysis or adjustments in marketing or pricing. 
                        """)
                    best_sellers_viz.product_analysis_app2(df)
            
    else:
        st.warning("There is no Total revenue or Product name or Cases sold columns, so visualizing can not be ready")
    
    if "Cases sold" in columns and "Total revenue" in columns:
        with st.container(border=True):
            col11, col12 = st.columns([10, 0.45])
            with col11:
                st.markdown("""
                <style>
                .big-font {
                    font-size:20px !important;
                }</style>""", unsafe_allow_html=True)
                st.markdown('<p class="big-font">Relationship between Cases Sold and Total Revenue</p>', unsafe_allow_html=True)
            with col12:
                if st.button("🛈", key=436, help="Get some plot information", use_container_width=False):
                    #if render_circle_button(22):
                    condition = True
                else:
                    condition = False
                # Check the state of the button
            if condition == True:
                st.markdown("""
                This chart demonstrates the direct relationship between the number of cases sold and the total revenue generated. Analyze this to:
                * **Identify Top Performing Products:**  Products with higher cases sold and larger bubble sizes contribute significantly to overall revenue.
                * **Track Sales Performance:**  Monitor sales trends to understand which products are driving revenue growth.
                * **Set Sales Targets:**  Use this relationship to set realistic sales targets and revenue goals.
                """)
            
            best_sellers_viz.create_cases_revenue_relationship_plot(df)
    else:
        st.warning("There is no Total revenue or Cases sold columns, so visualizing can not be ready")
    
    #wih cc2:
    # bar_chart()
    if "Category name" in columns and "Wholesale price" in columns and "Retail price" in columns:
        with st.container(border=True):
            col11, col12 = st.columns([10, 0.45])
            with col11:
                st.markdown("""
                <style>
                .big-font {
                    font-size:20px !important;
                }</style>""", unsafe_allow_html=True)
                st.markdown('<p class="big-font">Average Price Comparison by Category</p>', unsafe_allow_html=True)
            with col12:
                if st.button("🛈", key=437, help="Get some plot information", use_container_width=False):
                    #if render_circle_button(22):
                    condition = True
                else:
                    condition = False
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
                    font-size: 17px;
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
                tab1, tab2 = st.tabs(["Wholesale Price", "Retail Price"])
                with tab1:
                    if condition == True:
                        st.markdown("""
                    This chart visually compares average wholesale prices across categories, revealing which have higher or lower prices. Businesses can use this to:
                    * **Analyze Pricing Structure:**  Identify categories needing potential price adjustments.
                    * **Gain Profitability Insights:** Understand potential margins for each category, guiding sourcing, pricing, and inventory decisions.
                    * **Spot Discrepancies:** Investigate significantly different prices to uncover opportunities for cost optimization or pricing adjustments. 
                    """)
                    best_sellers_viz.price_comparison_app1(df)
                with tab2:
                    if condition == True:
                        st.markdown("""
                    This chart showcases the average retail prices across different product categories. By comparing these averages, businesses can:
                    * **Assess Competitive Pricing:** Evaluate how their retail prices stack up against the average for each category, enabling them to adjust pricing for greater competitiveness.
                    * **Identify Premium Categories:** Determine categories where higher prices are generally accepted, allowing for potential premium pricing strategies.
                    * **Understand Consumer Affordability:** Gain insights into the affordability of products within each category based on average retail prices, informing marketing and sales strategies.
                    """)
                    best_sellers_viz.price_comparison_app2(df)
            #_
            
    else:
        st.warning("There is no Category name or Wholesale price or Retail price columns, so visualizing can not be ready")
    
    if "Total revenue" in columns and "Product name" in columns:
        with st.container(border=True):
            col11, col12 = st.columns([10, 0.45])
            with col11:
                st.markdown("""
                <style>
                .big-font {
                    font-size:20px !important;
                }</style>""", unsafe_allow_html=True)
                st.markdown('<p class="big-font">Revenue Analysis</p>', unsafe_allow_html=True)
            with col12:
                if st.button("🛈", key=438, help="Get some plot information", use_container_width=False):
                    #if render_circle_button(22):
                    condition = True
                else:
                    condition = False
            with stylable_container(
            key="custom-tabs-big-button",
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
                tab1, tab2 = st.tabs(["Revenue vs. Profit", "Revenue Breakdown by Category"])
                with tab1:
                    if condition == True:
                        st.markdown("""*Visualizing the relationship between total revenue and profit for different products offers a powerful tool for businesses to assess product performance and profitability. This allows for the identification of high-performing products, the detection of potential issues, and the discovery of trends, ultimately facilitating strategic decision-making regarding pricing, cost management, and marketing efforts.* """)
                    best_sellers_viz.create_revenue_vs_profit_plot1(df)
                with tab2:
                    if condition == True:
                        st.markdown("""*Pie charts offer a powerful way to visualize revenue distribution across different categories, providing insights into the proportion each category contributes to the total. By highlighting the largest slices, businesses can quickly identify their key revenue drivers and make strategic decisions based on this understanding. This visual comparison of categories also facilitates tracking changes in revenue distribution over time, informing businesses about shifting consumer preferences and market trends.*""")
                    best_sellers_viz.create_revenue_vs_profit_plot2(df)
                # Check the state of the button
            
    else:
        st.warning("There is no Total revenue or Product name columns, so visualizing can not be ready")
    