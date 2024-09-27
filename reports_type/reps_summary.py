import streamlit as st
from streamlit_extras.stylable_container import stylable_container
from visualizations import reps_summary_viz
from side_func import get_csv_columns




def report_func(df):
    
    columns = get_csv_columns(df)
    reps_summary_viz.preprocess_data(df)
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
    #if "Orders" in columns and "Total revenue" in columns and "Cases sold" in columns:
    #    with st.container(border=True):
    #        col11, col12 = st.columns([10, 0.50])
    #        with col11:
    #            st.markdown("""
    #            <style>
    #            .big-font {
    #                font-size:20px !important;
    #            }</style>""", unsafe_allow_html=True)
    #            st.markdown('<p class="big-font">Revenue Drivers: Orders and Cases Sold</p>', unsafe_allow_html=True)
    #        with col12:
    #            if st.button("🛈", key=471, help="Get some plot information", use_container_width=False):
    #                #if render_circle_button(22):
    #                condition = True
    #            else:
    #                condition = False
    #        with stylable_container(
    #        key="custom-tabs1-button",
    #        css_styles=["""
    #            button {
    #                background-color: #ffffff;
    #                border: 2px solid #ffffff;
    #                color: #5f6267;
    #                padding: 0px;
    #                text-align: center;
    #                text-decoration: none;
    #                border-radius: 0%;
    #                font-size: 19px;
    #                margin: 4px 2px;
    #                border-style: solid;
    #                width: 150px;
    #                height: 30px;
    #                line-height: 30px;
    #                position: relative;
    #            }""",
    #            """
    #            button:hover {
    #                background-color: #ffffff;
    #                color: #409A65;
    #            }""",
    #            """
    #            button:focus {
    #                background-color: #ffffff;
    #                color: #409A65;
    #                border: 2px #ffffff;
    #            }
    #            """],
    #        ):
    #            tab1, tab2 = st.tabs(["Orders vs. Revenue", "Cases Sold vs. Revenue"])
    #            with tab1:
    #                if condition == True:
    #                    st.markdown("""
    #                These scatter plots analyze the relationships between revenue, orders placed, and cases sold. Explore these visualizations to identify key revenue drivers and understand how order volume and sales volume individually influence your bottom line. This can guide your sales strategies for maximizing revenue growth.
    #                """)
    #                reps_summary_viz.plot_sales_relationships1(df)
    #            with tab2:
    #                if condition == True:
    #                    st.markdown("""
    #                These scatter plots analyze the relationships between revenue, orders placed, and cases sold. Explore these visualizations to identify key revenue drivers and understand how order volume and sales volume individually influence your bottom line. This can guide your sales strategies for maximizing revenue growth.
    #                """)
    #                reps_summary_viz.plot_sales_relationships2(df)
    #else:
    #    st.warning("There is no Orders or Total revenue or Cases sold columns, so visualizing can not be ready")
    
    if "Date" in columns and "Role" in columns and "Total revenue" in columns:
        with st.container(border=True):
            col11, col12 = st.columns([10, 0.50])
            with col11:
                st.markdown("""
                <style>
                .big-font {
                    font-size:20px !important;
                }</style>""", unsafe_allow_html=True)
                st.markdown('<p class="big-font">Revenue Trends: Monthly Performance by Role</p>', unsafe_allow_html=True)
            with col12:
                if st.button("🛈", key=465, help="Get some plot information", use_container_width=False):
                    #if render_circle_button(22):
                    condition = True
                else:
                    condition = False
                # Check the state of the button
            if condition == True:
                st.markdown("""
                This bar chart presents a breakdown of revenue generated each month, categorized by sales role. Analyze these trends to identify periods of strong performance, potential seasonal variations, and opportunities for targeted improvements in specific months or for particular roles. 
                """)
            reps_summary_viz.plot_revenue_by_month_and_role(df)
    else:
        st.warning("There is no Date or Role or Total revenue columns, so visualizing can not be ready")
    
    if "Date" in columns:
        with st.container(border=True):
            col11, col12 = st.columns([10, 0.50])
            with col11:
                st.markdown("""
                <style>
                .big-font {
                    font-size:20px !important;
                }</style>""", unsafe_allow_html=True)
                st.markdown('<p class="big-font">Sales Patterns: Cases Sold by Day of the Week</p>', unsafe_allow_html=True)
            with col12:
                if st.button("🛈", key=466, help="Get some plot information", use_container_width=False):
                    #if render_circle_button(22):
                    condition = True
                else:
                    condition = False
                # Check the state of the button
            if condition == True:
                st.markdown("""
                This line chart presents the number of cases sold for each day of the week, highlighting the weekly sales trend. By analyzing these patterns, you can identify peak sales days, understand customer behavior, and optimize resource allocation, such as staffing and marketing efforts, to align with weekly sales trends.
                """)
            reps_summary_viz.plot_cases_sold_by_day_of_week(df)
    else:
        st.warning("There is no Date column, so visualizing can not be ready")
    
    if "Date" in columns and "Total revenue" in columns and "Role" in columns:
        with st.container(border=True):
            col11, col12 = st.columns([10, 0.50])
            with col11:
                st.markdown("""
                <style>
                .big-font {
                    font-size:20px !important;
                }</style>""", unsafe_allow_html=True)
                st.markdown('<p class="big-font">Revenue Trends: Monthly Performance by Role</p>', unsafe_allow_html=True)
            with col12:
                if st.button("🛈", key=467, help="Get some plot information", use_container_width=False):
                    #if render_circle_button(22):
                    condition = True
                else:
                    condition = False
                # Check the state of the button
            if condition == True:
                st.markdown("""
                This line chart tracks the revenue generated by Merchandisers and Sales Representatives each month, allowing you to visualize revenue fluctuations and compare performance trends between roles. Analyze these trends to identify seasonal patterns, the impact of sales strategies, and opportunities for growth.
                """)
            reps_summary_viz.plot_revenue_trend_by_month_and_role(df)
    else:
        st.warning("There is no Date or Total revenue or Role columns, so visualizing can not be ready")
    
    #wih cc2:
    if "Name" in columns and "Visits" in columns and "Travel distance" in columns:
        with st.container(border=True):
            col11, col12 = st.columns([10, 0.50])
            with col11:
                st.markdown("""
                <style>
                .big-font {
                    font-size:20px !important;
                }</style>""", unsafe_allow_html=True)
                st.markdown('<p class="big-font">Individual Performance: Visits and Travel</p>', unsafe_allow_html=True)
            with col12:
                if st.button("🛈", key=468, help="Get some plot information", use_container_width=False):
                    #if render_circle_button(22):
                    condition = True
                else:
                    condition = False
                # Check the state of the button
            if condition == True:
                st.markdown("""
                This bar chart provides a comparative view of the total visits and travel distance covered by each sales representative. By analyzing individual performance metrics, you can identify top performers, potential areas for improvement in travel efficiency, and opportunities for optimized resource allocation.
                """)
            reps_summary_viz.plot_visits_and_travel_distance_by_name(df)
    else:
        st.warning("There is no Name or Visits or Travel distance columns, so visualizing can not be ready")
    
    #if "Visits" in columns and "Orders" in columns:
    #    with st.container(border=True):
    #        col11, col12 = st.columns([10, 0.50])
    #        with col11:
    #            st.markdown("""
    #            <style>
    #            .big-font {
    #                font-size:20px !important;
    #            }</style>""", unsafe_allow_html=True)
    #            st.markdown('<p class="big-font">Visits vs. Orders: Exploring the Relationship</p>', unsafe_allow_html=True)
    #        with col12:
    #            if st.button("🛈", key=469, help="Get some plot information", use_container_width=False):
    #                #if render_circle_button(22):
    #                condition = True
    #            else:
    #                condition = False
    #            # Check the state of the button
    #        if condition == True:
    #            st.markdown("""
    #            This scatter plot, enhanced with a regression line, visualizes the relationship between the number of visits made by sales representatives and the number of orders generated. Analyze this visualization to understand the correlation between visits and orders, identify potential outliers, and gain insights into the effectiveness of sales efforts.
    #            The trendline represents the best-fit linear relationship between visits and orders. The R² value indicates how well the trendline fits the data, with values closer to 1 suggesting a stronger relationship.
    #            """)
    #        reps_summary_viz.plot_orders_vs_visits_with_regression(df)
    #else:
    #    st.warning("There is no Visits or Orders columns, so visualizing can not be ready")
    
    #if "Role" in columns and "Visits" in columns and "Orders" in columns and "Cases sold" in columns:
    #    with st.container(border=True):
    #        col11, col12 = st.columns([10, 0.50])
    #        with col11:
    #            st.markdown("""
    #            <style>
    #            .big-font {
    #                font-size:20px !important;
    #            }</style>""", unsafe_allow_html=True)
    #            st.markdown('<p class="big-font">Performance Metrics by Role</p>', unsafe_allow_html=True)
    #        with col12:
    #            if st.button("🛈", key=470, help="Get some plot information", use_container_width=False):
    #                #if render_circle_button(22):
    #                condition = True
    #            else:
    #                condition = False
    #            # Check the state of the button
    #        if condition == True:
    #            st.markdown("""
    #            This bar chart provides a comparative overview of key performance metrics (visits, orders, and cases sold) across different sales roles. Analyzing these metrics together can help you identify which roles are excelling in specific areas and pinpoint opportunities for improvement. 
    #            """)
    #        reps_summary_viz.plot_multiple_metrics_by_role(df)
    #else:
    #    st.warning("There is no Role or Visits or Orders or Cases sold columns, so visualizing can not be ready")
    
    #if "Cases sold" in columns and "Total revenue" in columns and "Visits" in columns and "Travel distance" in columns:
    #    with st.container(border=True):
    #        col11, col12 = st.columns([10, 0.50])
    #        with col11:
    #            st.markdown("""
    #            <style>
    #            .big-font {
    #                font-size:20px !important;
    #            }</style>""", unsafe_allow_html=True)
    #            st.markdown('<p class="big-font">Revenue vs. Cases Sold: Insights from Visits and Travel</p>', unsafe_allow_html=True)
    #        with col12:
    #            if st.button("🛈", key=1471, help="Get some plot information", use_container_width=False):
    #                #if render_circle_button(22):
    #                condition = True
    #            else:
    #                condition = False
    #            # Check the state of the button
    #        if condition == True:
    #            st.markdown("""
    #            This interactive scatter plot provides a comprehensive view of your sales data. Explore the relationship between revenue and cases sold, with the size of each point representing visit frequency and color indicating travel distance. This visualization allows you to uncover deeper insights into the factors influencing sales performance and identify potential areas for optimization.  
    #            """)
    #        reps_summary_viz.plot_revenue_vs_cases_sold_with_size_and_color(df)
    #else:
    #    st.warning("There is no Cases sold or Total revenue or Visits or Travel distance columns, so visualizing can not be ready")
    
    if True:
        with st.container(border=True):
            col11, col12 = st.columns([10, 0.50])
            with col11:
                st.markdown("""
                <style>
                .big-font {
                    font-size:20px !important;
                }</style>""", unsafe_allow_html=True)
                st.markdown('<p class="big-font">Individual Performance: Visits and Travel</p>', unsafe_allow_html=True)
            with col12:
                if st.button("🛈", key=3468, help="Get some plot information", use_container_width=False):
                    #if render_circle_button(22):
                    condition = True
                else:
                    condition = False
                # Check the state of the button
            if condition == True:
                st.markdown("""
                This bar chart provides a comparative view of the total visits and travel distance covered by each sales representative. By analyzing individual performance metrics, you can identify top performers, potential areas for improvement in travel efficiency, and opportunities for optimized resource allocation.
                """)
            reps_summary_viz.total_revenue_and_conversion_rate(df)
            reps_summary_viz.Total_Visits_vs_Total_Revenue(df)
    else:
        st.warning("There is no Cases sold or Total revenue or Visits or Travel distance columns, so visualizing can not be ready")
    