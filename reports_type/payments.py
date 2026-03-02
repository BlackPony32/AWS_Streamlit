import streamlit as st
from streamlit_extras.stylable_container import stylable_container
from visualizations import payments_viz
from side_func import get_csv_columns



def report_func(df):
    #st.success("This report is new, so visualizations are not available yet")
    columns = get_csv_columns(df)

    payments_viz.preprocess_data(df)
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
    
    if "Business Name" in columns and "Payment Amount" in columns and "Order Balance" in columns:
        try:
            with st.container(border=True):
                col11, col12 = st.columns([10, 0.50])
                with col11:
                    st.markdown("""
                        <style>
                        .big-font {
                            font-size:20px !important;
                        }
                        </style>""", unsafe_allow_html=True)
                    st.markdown('<p class="big-font">Payments vs. Outstanding Balance by Business</p>', unsafe_allow_html=True)

                with col12:
                    # Help button logic
                    condition = st.button("🛈", key=465, help="Get plot information", use_container_width=False)

                if condition:
                    st.markdown("""
                        This grouped bar chart compares the **Total Payments Received** against the **Remaining Order Balance** for each business. 
                        It helps identify your most profitable customers versus those with high outstanding debt, 
                        allowing for better credit control and collection prioritization.
                        """)

                # Call the visualization function
                payments_viz.Business_Payment_Insights(df)
        except Exception as e:
            print("Error in Business_Payment_Insights:", e)
            st.success("This visualization is temporarily unavailable")    
    else:
        #print(e)
        st.warning("There is some error with plot, so visualizing can not be ready")
        


    #required_cols = ["Payment Status", "Payment Method", "Business Name", "Payment Amount"]
    #if all(col in df.columns for col in required_cols):
    #    try:
    #        with st.container(border=True):
    #            col11, col12 = st.columns([10, 0.50])
    #            with col11:
    #                st.markdown("""
    #                    <style>
    #                    .big-font {
    #                        font-size:20px !important;
    #                    }
    #                    </style>""", unsafe_allow_html=True)
    #                st.markdown('<p class="big-font">Financial Distribution: Status, Method, and Impact</p>', unsafe_allow_html=True)
#
    #            with col12:
    #                # Help button logic
    #                condition = st.button("🛈", key=466, help="Get plot information", use_container_width=False)
#
    #            if condition:
    #                st.info("""
    #                **About this Plot:**
    #                This is a **Hierarchical Sunburst Chart** that visualizes your revenue streams across three dimensions:
    #                1. **Center Circle (Level 1):** Shows the total dollar value categorized by **Payment Status** (e.g., Paid vs. Overdue).
    #                2. **Outer Ring (Level 2):** Breaks down each status by the **Payment Method** used (e.g., identifying which methods are most common for overdue orders).
    #                3. **Interactive Drill-down:** Click on any category to zoom in. This helps you identify if specific payment methods (like Checks) are contributing more to your "Overdue" or "Unpaid" balances than others.
    #                """)
#
    #            # Call the visualization function
    #            payments_viz.Payment_Distribution_Treemap(df)
    #    except Exception as e:
    #        print("Error in Payment_Distribution_Treemap:", e)
    #        st.success("This visualization is temporarily unavailable")    
    #else:
    #    #print(e)
    #    st.warning("There is some error with plot, so visualizing can not be ready")


    