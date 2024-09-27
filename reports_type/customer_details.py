import streamlit as st
from streamlit_extras.stylable_container import stylable_container
from visualizations import customer_details_viz
from side_func import get_csv_columns




def report_func(df):
    
    columns = get_csv_columns(df)
    customer_details_viz.preprocess_data(df)
    
    if "Group" in columns and "Total orders" in columns and "Total sales" in columns:
        with st.container(border=True):
            col11, col12 = st.columns([10, 0.50])
            with col11:
                st.markdown("""
                <style>
                .big-font {
                    font-size:20px !important;
                }</style>""", unsafe_allow_html=True)
                st.markdown('<p class="big-font">Comparison of Total Orders and Sales by Customer Group</p>', unsafe_allow_html=True)
            with col12:
                if st.button("🛈", key=500, help="Get some plot information", use_container_width=False):
                    #if render_circle_button(22):
                    condition = True
                else:
                    condition = False
                # Check the state of the button
            if condition == True:
                st.markdown("""
                These visualizations compare total orders and sales for each customer group, revealing valuable insights about your most important customer segments. Use this data to identify high-value customers, understand purchasing behavior, and optimize your sales and marketing strategies.
                """)
            customer_details_viz.plot_orders_and_sales_plotly(df)
    else:
        st.warning("There is no Group or Total orders or Total sales columns, so visualizing can not be ready")
    
    if "Payment terms" in columns:
        with st.container(border=True):
            col11, col12 = st.columns([10, 0.50])
            with col11:
                st.markdown("""
                <style>
                .big-font {
                    font-size:20px !important;
                }</style>""", unsafe_allow_html=True)
                st.markdown('<p class="big-font">Payment Terms: Understanding Client Preferences</p>', unsafe_allow_html=True)
            with col12:
                if st.button("🛈", key=501, help="Get some plot information", use_container_width=False):
                    #if render_circle_button(22):
                    condition = True
                else:
                    condition = False
                # Check the state of the button
            if condition == True:
                st.markdown("""
            This visualization shows how your clients are distributed across different payment terms. Use these insights to optimize your cash flow management, tailor your offerings to different customer segments, and make informed decisions about credit risk.
            """)
            customer_details_viz.bar_plot_sorted_with_percentages(df)
    else:
        st.warning("There is no Payment terms column, so visualizing can not be ready")
    
    #wih cc2:
    if "Total sales" in columns:
        with st.container(border=True):
            col11, col12 = st.columns([10, 0.50])
            with col11:
                st.markdown("""
                <style>
                .big-font {
                    font-size:20px !important;
                }</style>""", unsafe_allow_html=True)
                st.markdown('<p class="big-font">Sales Value Distribution: Insights for Growth</p>', unsafe_allow_html=True)
            with col12:
                if st.button("🛈", key=502, help="Get some plot information", use_container_width=False):
                    #if render_circle_button(22):
                    condition = True
                else:
                    condition = False
                # Check the state of the button
            if condition == True:
                st.markdown("""
                This visualization reveals how non-zero total sales values are distributed. Use these insights to refine your pricing and promotion strategies, enhance sales forecasting, optimize product development, and effectively manage potential risks.
                """)
            customer_details_viz.create_interactive_non_zero_sales_plot(df)
    else:
        st.warning("There is no Total sales column, so visualizing can not be ready")
    
        
    if "Total sales" in columns and "Group" in columns and "Billing state" in columns:
        with st.container(border=True):
            col11, col12 = st.columns([10, 0.50])
            with col11:
                st.markdown("""
                <style>
                .big-font {
                    font-size:20px !important;
                }</style>""", unsafe_allow_html=True)
                st.markdown('<p class="big-font">Average Total Sales by Customer Group and State</p>', unsafe_allow_html=True)
            with col12:
                if st.button("🛈", key=503, help="Get some plot information", use_container_width=False):
                    #if render_circle_button(22):
                    condition = True
                else:
                    condition = False
                # Check the state of the button
            if condition == True:
                st.markdown("""
                This heatmap reveals average total sales across customer groups and states. Use it to:
                - **Pinpoint high-performing segments and regions.**
                - **Identify areas for growth and optimization.**
                - **Develop targeted sales and marketing strategies.**
                - **Efficiently allocate resources and manage inventory.**
                """)
            customer_details_viz.create_interactive_average_sales_heatmap(df)
            

    else:
        st.warning("There is no Total sales or Group or Billing state columns, so visualizing can not be ready")
        
    if "Total sales" in columns and "Group" in columns and "Billing state" in columns:
        with st.container(border=True):
            col11, col12 = st.columns([10, 0.50])
            with col11:
                st.markdown("""
                <style>
                .big-font {
                    font-size:20px !important;
                }</style>""", unsafe_allow_html=True)
                st.markdown('<p class="big-font">Total Sales Trend by Customer Group</p>', unsafe_allow_html=True)
            with col12:
                if st.button("🛈", key=504, help="Get some plot information", use_container_width=False):
                    #if render_circle_button(22):
                    condition = True
                else:
                    condition = False
                # Check the state of the button
            if condition == True:
                st.markdown("""
                This chart is useful for business as it highlights the sales distribution across different customer groups.
                By identifying which groups contribute the most and least to total sales, businesses can prioritize high-value customers, explore potential in low-performing groups, and develop targeted strategies for each segment to maximize revenue opportunities.
                """)

            #This line chart gives a clear picture of how total sales compare across different customer groups, making it easy to see which groups are performing better or worse.
            customer_details_viz.create_sales_trend_by_group(df)
            
    else:
        st.warning("There is no Total sales or Group or Billing state columns, so visualizing can not be ready")
