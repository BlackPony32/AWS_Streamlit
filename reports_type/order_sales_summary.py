import streamlit as st
from streamlit_extras.stylable_container import stylable_container
from visualizations import order_sales_summary_viz
from side_func import get_csv_columns




def report_func(df):
    
    columns = get_csv_columns(df)
    order_sales_summary_viz.preprocess_data(df)
    
    if "Customer" in columns and "Product name" in columns and "Created at" in columns:
        with st.container(border=True):
            col11, col12 = st.columns([10, 0.45])
            with col11:
                st.markdown("""
                <style>
                .big-font {
                    font-size:20px !important;
                }</style>""", unsafe_allow_html=True)
                st.markdown('<p class="big-font">Monthly Sales Trend</p>', unsafe_allow_html=True)
            with col12:
                if st.button("🛈", key=415, help="Get some plot information", use_container_width=False):
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
                tab1, tab2 = st.tabs(["Total Sales", "Order Distribution"])
                with tab1:
                    if condition == True:
                        st.markdown("""
                        This bar chart highlights the top 10 customers by sales amount, providing insights into:
                        * **Identifying Key Customers:** Pinpoint valuable customers to prioritize relationships and tailor marketing efforts.
                        * **Resource Allocation:** Allocate resources efficiently, ensuring top customers receive premium service and support.
                        * **Sales Strategy Development:** Develop targeted sales strategies to increase sales from key customers.
                        """)
                    order_sales_summary_viz.visualize_sales_trends1(df)
                with tab2:
                    if condition == True:
                        st.markdown("""
                    This bar chart shows the number of orders for each product, providing insights into:
                    * **Product Popularity:** Identify products with high order volumes, indicating popularity or demand.
                    * **Inventory Planning:** Use order volume to inform inventory management and prevent stock shortages for popular items. 
                    * **Performance Comparison:** See which products have relatively low order numbers, which might suggest areas for improvement.
                    """)
                    order_sales_summary_viz.visualize_sales_trends2(df)
    else:
        st.warning("There is no Customer or Product name or Created at columns, so visualizing can not be ready")
    
    if "Product name" in columns and "Grand total" in columns:
        with st.container(border=True):
            col11, col12 = st.columns([10, 0.45])
            with col11:
                st.markdown("""
                <style>
                .big-font {
                    font-size:20px !important;
                }</style>""", unsafe_allow_html=True)
                st.markdown('<p class="big-font">Total sales and order distribution by product</p>', unsafe_allow_html=True)
            with col12:
                if st.button("🛈", key=416, help="Get some plot information", use_container_width=False):
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
                tab1, tab2 = st.tabs(["Top Customers", "Monthly Trend"])
                with tab1:
                    if condition == True:
                        st.markdown("""
                        This pie chart presents the share of total sales revenue generated by each product. It helps you:
                        * **Identify Top Performers:** Quickly see which products contribute the most to overall revenue.
                        * **Prioritize Product Focus:** Determine where to concentrate marketing and sales efforts for maximum impact.
                        * **Analyze Performance Trends:** Track changes in product sales contributions over time. 
                        """)
                    order_sales_summary_viz.visualize_product_analysis1(df)
                with tab2:
                    if condition == True:
                        st.markdown("""
                        This bar chart shows the number of orders for each product, providing insights into:
                        * **Product Popularity:** Identify products with high order volumes, indicating popularity or demand.
                        * **Inventory Planning:** Use order volume to inform inventory management and prevent stock shortages for popular items. 
                        * **Performance Comparison:** See which products have relatively low order numbers, which might suggest areas for improvement.
                        """)
                    order_sales_summary_viz.visualize_product_analysis2(df)
    else:
        st.warning("There is no Product name or Grand total columns, so visualizing can not be ready")
    
    if "Discount type" in columns and "Total invoice discount" in columns and "Customer" in columns:
        with st.container(border=True):
            col11, col12 = st.columns([10, 0.45])
            with col11:
                st.markdown("""
                <style>
                .big-font {
                    font-size:20px !important;
                }</style>""", unsafe_allow_html=True)
                st.markdown('<p class="big-font">Distribution of Discount Amount</p>', unsafe_allow_html=True)
            with col12:
                if st.button("🛈", key=417, help="Get some plot information", use_container_width=False):
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
                tab1, tab2 = st.tabs(["Top Customers", "By Type"])
                with tab1:
                    if condition == True:
                        st.markdown("""
                        This chart shows the customers receiving the highest total discounts. It helps to:
                        - **Align with Customer Strategies:** Ensure discounts align with business goals.
                        - **Identify Negotiation Patterns:** Spot disparities or patterns in customer agreements.
                        """)
                    order_sales_summary_viz.visualize_discount_analysis1(df)
                with tab2:
                    if condition == True:
                        st.markdown("""
                        ## Top Discount Recipients 
                        This chart shows the customers receiving the highest total discounts. It helps to:
                        - **Align with Customer Strategies:** Ensure discounts align with business goals.
                        - **Identify Negotiation Patterns:** Spot disparities or patterns in customer agreements.
                        """)
                    order_sales_summary_viz.visualize_discount_analysis2(df)
    else:
        st.warning("There is no Discount type or Total invoice discount or Customer columns, so visualizing can not be ready")
    
    #wih cc2:
    # bar_chart()
    if "Delivery status" in columns and "Delivery methods" in columns:
        with st.container(border=True):
            col11, col12 = st.columns([10, 0.45])
            with col11:
                st.markdown("""
                <style>
                .big-font {
                    font-size:20px !important;
                }</style>""", unsafe_allow_html=True)
                st.markdown('<p class="big-font">Delivery analysis</p>', unsafe_allow_html=True)
            with col12:
                if st.button("🛈", key=418, help="Get some plot information", use_container_width=False):
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
                tab1, tab2 = st.tabs(["By Status", "By Method"])
                with tab1:
                    if condition == True:
                        st.markdown("""
                        ## Delivery Status Insights
                        This pie chart displays the proportion of orders for each delivery status. It helps you:
                        * **Monitor Delivery Efficiency:** Track the percentage of "Delivered" orders over time to assess overall efficiency.
                        * **Spot Potential Issues:** A high percentage of "Cancelled" or "Returned" orders might indicate issues that require further investigation.
                        """)
                    order_sales_summary_viz.visualize_delivery_analysis1(df)
                with tab2:
                    if condition == True:

                        st.markdown("""
                        ## Delivery Method Insights
                        This pie chart shows the distribution of orders across different delivery methods, helping you understand:
                        * **Customer Preferences:** Which delivery methods are most popular among your customers?
                        * **Operational Efficiency:** Are certain delivery methods used more frequently? This information can inform resource allocation and logistics planning. 
                        """)
                    order_sales_summary_viz.visualize_delivery_analysis2(df)
    else:
        st.warning("There is no Delivery status or Delivery methods columns, so visualizing can not be ready")
    
    if "Payment status" in columns:
        with st.container(border=True):
            col11, col12 = st.columns([10, 0.45])
            with col11:
                st.markdown("""
                <style>
                .big-font {
                    font-size:20px !important;
                }</style>""", unsafe_allow_html=True)
                st.markdown('<p class="big-font">Payment Status Insights</p>', unsafe_allow_html=True)
            with col12:
                if st.button("🛈", key=419, help="Get some plot information", use_container_width=False):
                    #if render_circle_button(22):
                    condition = True
                else:
                    condition = False
                # Check the state of the button
            if condition == True:
                st.markdown("""
                This chart shows the distribution of orders by payment status. Use it to:
                * **Identify Payment Processing Issues:** Spot any anomalies in payment status distribution.
                * **Track Payment Trends:** Monitor changes in payment behavior over time.
                * **Gain Insights into Refund Frequency:** Understand how often refunds are processed.
                """)
            order_sales_summary_viz.visualize_payment_analysis(df)
    else:
        st.warning("There is no Payment status column, so visualizing can not be ready")
    
    if "Product name" in columns and "Grand total" in columns and "QTY" in columns and "Delivery status"in columns:
        with st.container(border=True):
            col11, col12 = st.columns([10, 0.45])
            with col11:
                st.markdown("""
                <style>
                .big-font {
                    font-size:20px !important;
                }</style>""", unsafe_allow_html=True)
                st.markdown('<p class="big-font">Quantity vs. Amount Insights. Number of Orders by Product and Delivery Status</p>', unsafe_allow_html=True)
            with col12:
                if st.button("🛈", key=4020, help="Get some plot information", use_container_width=False):
                    #if render_circle_button(22):
                    condition = True
                else:
                    condition = False
            with stylable_container(
            key="custom-tabs2-button",
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
                    width: 165px;
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
                tab1, tab2 = st.tabs(["Quantity vs. Amount", "Orders by Product & Status"])
                with tab1:
                    if condition == True:
                        st.markdown("""
                        This plot reveals how quantity sold relates to sales amount. Analyze trends, outliers, and product performance to make informed pricing and inventory decisions.
                        """)
                    order_sales_summary_viz.visualize_combined_analysis1(df)
                with tab2:
                    if condition == True:

                        st.markdown("""
                        This chart compares order volumes and fulfillment status. Identify potential bottlenecks, optimize inventory, and improve customer service by understanding product-level fulfillment patterns. 
                        """)
                    order_sales_summary_viz.visualize_combined_analysis2(df)
    else:
        st.warning("There is no Grand total or Product name or Quantity or Delivery status columns, so visualizing can not be ready")
