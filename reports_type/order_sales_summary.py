import streamlit as st
from streamlit_extras.stylable_container import stylable_container
from visualizations import order_sales_summary_viz
from side_func import get_csv_columns




def report_func(df):
    
    columns = get_csv_columns(df)
    order_sales_summary_viz.preprocess_data(df)
    
    if "Customer" in columns and "Grand Total" in columns and "Product Name" in columns and "Date Created" in columns:
        try:
            with st.container(border=True):
                col11, col12 = st.columns([10, 0.50])
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
                    tab1, tab2 = st.tabs(["Top Customers", "Monthly Trend"])
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
                        This line plot shows the Monthly Sales Trend over time, allowing you to quickly identify patterns, such as seasonal fluctuations or significant changes in sales. 
                        It helps in making informed decisions for planning inventory, marketing strategies, and resource allocation.
                        """)
                        order_sales_summary_viz.visualize_sales_trends2(df)
        except Exception as e:
            print("Error in visualize_sales_trends2:", e)
            st.success("This visualization is temporarily unavailable")
    else:
        st.warning("There is no Customer or Product name or Created at columns, so visualizing can not be ready")
    
    if "Product Name" in columns and "Grand Total" in columns:
        try:
            with st.container(border=True):
                col11, col12 = st.columns([10, 0.50])
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
        except Exception as e:
            print("Error in visualize_product_analysis2:", e)
            st.success("This visualization is temporarily unavailable")
    else:
        st.warning("There is no Product name or Grand total columns, so visualizing can not be ready")
    
    if "Discount Type" in columns and "Total Invoice Discount" in columns and "Customer" in columns:
        try:
            with st.container(border=True):
                col11, col12 = st.columns([10, 0.50])
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
        except Exception as e:
            print("Error in visualize_discount_analysis2:", e)
            st.success("This visualization is temporarily unavailable")
    else:
        st.warning("There is no Discount type or Total invoice discount or Customer columns, so visualizing can not be ready")
    
    #wih cc2:
    # bar_chart()
    if "Delivery Status" in columns and "Delivery Methods" in columns:
        try:
            with st.container(border=True):
                col11, col12 = st.columns([10, 0.50])
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
        except Exception as e:
            print("Error in visualize_delivery_analysis2:", e)
            st.success("This visualization is temporarily unavailable")
    else:
        st.warning("There is no Delivery status or Delivery methods columns, so visualizing can not be ready")
    
    if "Payment Status" in columns:
        try:
            with st.container(border=True):
                col11, col12 = st.columns([10, 0.50])
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
        except Exception as e:
            print("Error in visualize_payment_analysis:", e)
            st.success("This visualization is temporarily unavailable")
    else:
        st.warning("There is no Payment status column, so visualizing can not be ready")
    
    if "Product Name" in columns and "Grand Total" in columns and "QTY" in columns and "Delivery Status"in columns:
        try:
            with st.container(border=True):
                col11, col12 = st.columns([10, 0.50])
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
        except Exception as e:
            print("Error in visualize_combined_analysis2:", e)
            st.success("This visualization is temporarily unavailable")
    else:
        st.warning("There is no Grand total or Product name or Quantity or Delivery status columns, so visualizing can not be ready")

    if "Date Created" in df.columns and "QTY" in df.columns and "Customer" in df.columns:
        try:
            with st.container(border=True):
                # --- Header & Filter ---
                col_header, col_btn = st.columns([9, 0.5])
                with col_header:
                    st.markdown("""<style>.big-font { font-size:20px !important; font-weight: bold; }</style>""", unsafe_allow_html=True)
                    st.markdown('<p class="big-font">Sales Velocity Report</p>', unsafe_allow_html=True)

                with col_btn:
                    if st.button("🛈", key="velocity_info_btn", help="Get plot information"):
                        condition = True
                    else:
                        condition = False

                time_filter = st.radio(
                    "Select Frequency:",
                    options=["Weekly (Sun)", "Daily", "Monthly"],
                    index=0,
                    horizontal=True,
                    label_visibility="collapsed",
                    key="velocity_time_filter"
                )

                # --- Calculate Data Once (Based on Filter) ---
                # This ensures Charts and Tab 3 Data are identical
                df_total_processed = order_sales_summary_viz.calculate_total_velocity(df, time_filter)
                df_store_processed = order_sales_summary_viz.calculate_store_velocity(df, time_filter)

                # --- Tabs ---
                with stylable_container(
                    key="velocity-tabs-button",
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
                        """button:hover { background-color: #ffffff; color: #409A65; }""",
                        """button:focus { background-color: #ffffff; color: #409A65; border: 2px #ffffff; }"""],
                ):
                    # Added "Dataset & Export" as the 3rd tab
                    tab1, tab2, tab3 = st.tabs(["Total Velocity Overview", "Store Velocity View", "Dataset & Export"])

                    with tab1:
                        if condition:
                            st.markdown(f"Showing total units sold aggregated by **{time_filter}**.")
                        order_sales_summary_viz.visualize_total_velocity(df_total_processed, time_filter)

                    with tab2:
                        if condition:
                            st.markdown(f"Showing units sold per store aggregated by **{time_filter}**.")
                        order_sales_summary_viz.visualize_store_velocity(df_store_processed, time_filter)

                    with tab3:
                        st.markdown("### Export Processed Data")
                        st.markdown(f"Below are the datasets generated using the **{time_filter}** logic selected above.")

                        col_d1, col_d2 = st.columns(2)

                        # --- Table 1: Total Velocity ---
                        with col_d1:
                            st.subheader("Total Velocity Data")
                            st.dataframe(df_total_processed, use_container_width=True, height=300)

                            csv_total = df_total_processed.to_csv(index=False).encode('utf-8')
                            st.download_button(
                                label="Download Total Velocity (CSV)",
                                data=csv_total,
                                file_name=f"total_velocity_{time_filter}.csv",
                                mime="text/csv",
                                key="dl_total"
                            )

                        # --- Table 2: Store Velocity ---
                        with col_d2:
                            st.subheader("Store Velocity Data")
                            st.dataframe(df_store_processed, use_container_width=True, height=300)

                            csv_store = df_store_processed.to_csv(index=False).encode('utf-8')
                            st.download_button(
                                label="Download Store Velocity (CSV)",
                                data=csv_store,
                                file_name=f"store_velocity_{time_filter}.csv",
                                mime="text/csv",
                                key="dl_store"
                            )

        except Exception as e:
            print("Error in Velocity Report visualization:", e)
            st.success("This visualization is temporarily unavailable")
    else:
        st.warning("The required columns ('Date Created', 'QTY', 'Customer') are missing, so the Velocity Report cannot be generated.")