import streamlit as st
from streamlit_extras.stylable_container import stylable_container
from visualizations import reps_details_viz
from side_func import get_csv_columns




def report_func(df):
    
    columns = get_csv_columns(df)
    reps_details_viz.preprocess_data(df)
    
    if "Total working hours" in columns and "Total visits" in columns and "Assigned customers" in columns and "Role"in columns:
        with st.container(border=True):
            col11, col12 = st.columns([10, 0.50])
            with col11:
                st.markdown("""
                <style>
                .big-font {
                    font-size:20px !important;
                }</style>""", unsafe_allow_html=True)
                st.markdown('<p class="big-font">Visit Distribution: Understanding Role Contributions</p>', unsafe_allow_html=True)
            with col12:
                if st.button("🛈", key=464, help="Get some plot information", use_container_width=False):
                    #if render_circle_button(22):
                    condition = True
                else:
                    condition = False
                # Check the state of the button
            if condition == True:
                st.markdown("""
            This interactive donut chart provides a clear picture of how total visits are distributed among your sales roles. By visualizing these proportions, you can gain a better understanding of each role's contribution to overall sales efforts. 
            """)
            reps_details_viz.analyze_sales_rep_efficiency(df)
    else:
        st.warning("There is no Total working hours or Total visits or Assigned customers or Role columns, so visualizing can not be ready")
    
    if "Role" in columns and "Active customers" in columns and "Total visits" in columns:
        with st.container(border=True):
            col11, col12 = st.columns([10, 0.50])
            with col11:
                st.markdown("""
                <style>
                .big-font {
                    font-size:20px !important;
                }</style>""", unsafe_allow_html=True)
                st.markdown('<p class="big-font">Active Customers vs. Total Visits (Sales Reps)</p>', unsafe_allow_html=True)
            with col12:
                if st.button("🛈", key=465, help="Get some plot information", use_container_width=False):
                    #if render_circle_button(22):
                    condition = True
                else:
                    condition = False
                # Check the state of the button
            if condition == True:
                st.markdown("""
                This scatter plot explores the relationship between the number of active customers a sales representative handles and their total number of visits.  By analyzing individual performance and overall trends, you can identify opportunities to optimize sales strategies, resource allocation, and potentially set more effective goals. 
                """)
            reps_details_viz.plot_active_customers_vs_visits(df)
    else:
        st.warning("There is no Role or Active customers or Total visits columns, so visualizing can not be ready")
    
    if "Total travel distance" in columns and "Total visits" in columns and "Role" in columns:
        with st.container(border=True):
            col11, col12 = st.columns([10, 0.50])
            with col11:
                st.markdown("""
                <style>
                .big-font {
                    font-size:20px !important;
                }</style>""", unsafe_allow_html=True)
                st.markdown('<p class="big-font">Travel Efficiency: Distance vs. Visits</p>', unsafe_allow_html=True)
            with col12:
                if st.button("🛈", key=466, help="Get some plot information", use_container_width=False):
                    #if render_circle_button(22):
                    condition = True
                else:
                    condition = False
                # Check the state of the button
            if condition == True:
                st.markdown("""
                This scatter plot shows the relationship between total travel distance and the number of visits. Each point represents a team member, colored by their role.
                Use this plot to identify trends, outliers, and opportunities to optimize travel routes.
                """)
            reps_details_viz.plot_travel_efficiency_line(df)
    else:
        st.warning("There is no Total travel distance or Total visits or Role columns, so visualizing can not be ready")
    
    #wih cc2:
    if "Total working hours" in columns and "Total break hours" in columns and "Total travel distance" in columns:
        with st.container(border=True):
            col11, col12 = st.columns([10, 0.50])
            with col11:
                st.markdown("""
                <style>
                .big-font {
                    font-size:20px !important;
                }</style>""", unsafe_allow_html=True)
                st.markdown('<p class="big-font">Workload and Travel: Insights into Top Performers</p>', unsafe_allow_html=True)
            with col12:
                if st.button("🛈", key=467, help="Get some plot information", use_container_width=False):
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
                    font-size: 19px;
                    margin: 4px 2px;
                    border-style: solid;
                    width: 130px;
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
                tab1, tab2 = st.tabs(["Pure Work Hours", "Total Travel Distance"])
                with tab1:
                    if condition == True:
                        st.markdown("""
                        These bar charts, separated into tabs for easy navigation, highlight the top 10 employees based on pure work hours and total travel distance. Use these visualizations to identify potential workload imbalances, analyze travel patterns, and explore ways to optimize efficiency and resource allocation.""")
                    reps_details_viz.analyze_work_hours_and_distance1(df)
                with tab2:
                    if condition == True:
                        st.markdown("""
                        These bar charts, separated into tabs for easy navigation, highlight the top 10 employees based on pure work hours and total travel distance. Use these visualizations to identify potential workload imbalances, analyze travel patterns, and explore ways to optimize efficiency and resource allocation.
                        """)
                    reps_details_viz.analyze_work_hours_and_distance2(df)
    else:
        st.warning("There is no Total working hours or Total break hours or Total travel distance columns, so visualizing can not be ready")
    
    if "Role" in columns and "Total visits" in columns and "Total photos" in columns:
        with st.container(border=True):
            col11, col12 = st.columns([10, 0.50])
            with col11:
                st.markdown("""
                <style>
                .big-font {
                    font-size:20px !important;
                }</style>""", unsafe_allow_html=True)
                st.markdown('<p class="big-font">Travel Efficiency: Distance vs. Visits</p>', unsafe_allow_html=True)
            with col12:
                if st.button("🛈", key=468, help="Get some plot information", use_container_width=False):
                    #if render_circle_button(22):
                    condition = True
                else:
                    condition = False
                # Check the state of the button
            if condition == True:
                st.markdown("""
                These scatter plots analyze the relationship between total visits and the number of photos taken by team members for each role. This visualization helps to understand engagement levels and photo-taking patterns.
                """)
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
                    width: 120px;
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
                reps_details_viz.plot_visits_vs_photos_separate(df)
    else:
        st.warning("There is no Role or Total visits or Total photos columns, so visualizing can not be ready")
    
    if "Role" in columns and "Assigned customers" in columns:
        with st.container(border=True):
            col11, col12 = st.columns([10, 0.50])
            with col11:
                st.markdown("""
                <style>
                .big-font {
                    font-size:20px !important;
                }</style>""", unsafe_allow_html=True)
                st.markdown('<p class="big-font">Assigned Customers per Sales Representative</p>', unsafe_allow_html=True)
            with col12:
                if st.button("🛈", key=469, help="Get some plot information", use_container_width=False):
                    #if render_circle_button(22):
                    condition = True
                else:
                    condition = False
                # Check the state of the button
            if condition == True:
                st.markdown("""
            The bar plot above shows the number of assigned customers per sales representative. This visualization helps to identify potential imbalances in workload or variations in customer assignments. By analyzing this distribution, you can make informed decisions to optimize sales territories and ensure a more balanced workload across your sales team.
            """)
            reps_details_viz.analyze_customer_distribution(df)
    else:
        st.warning("There is no Role or Assigned customers columns, so visualizing can not be ready")
        