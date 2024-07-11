import streamlit as st
import pandas as pd
import os
import openai
import httpx
import asyncio
import json
from dotenv import load_dotenv
import httpx
from fastapi import Response
import requests
import glob

from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor
from langchain_experimental.agents.agent_toolkits import create_csv_agent
from langchain.prompts import ChatPromptTemplate
from langchain_core.utils.function_calling import convert_to_openai_function
from langchain.agents.format_scratchpad import format_to_openai_function_messages
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain.agents.agent_types import AgentType

from pandasai.llm.openai import OpenAI
from pandasai import SmartDataframe, Agent

from visualizations import (
    third_party_sales_viz, order_sales_summary_viz, best_sellers_viz,
    reps_details_viz, reps_summary_viz, skus_not_ordered_viz,
    low_stock_inventory_viz, current_inventory_viz, top_customers_viz, customer_details_viz
)
from side_func import identify_file, get_file_name, get_csv_columns

load_dotenv()

fastapi_url = os.getenv('FASTAPI_URL')


st.set_page_config( page_icon='icon.ico', page_title="SimplyDepo report")
css='''
<style>
    section.main > div {max-width:75rem}
</style>
'''
st.markdown(css, unsafe_allow_html=True)


UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

def add_custom_css():
        st.markdown(
        """
        <style>
        .stButton button {
            background-color: #ffffff; /* White background */
            border: 2px solid #ffffff; /* White border */
            color: #4CAF50; /* Green text */
            padding: 0px; /* Adjust padding for size */
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 12px;
            margin: 4px 2px;
            cursor: pointer;
            border-radius: 50%; /* Makes the button circular */
            border-style: solid;
            width: 55px; /* Adjust width for size */
            height: 40px; /* Adjust height for size */
            line-height: 30px; /* Adjust line height for centering text */
            position: relative;
        }
        .stButton button:hover {
            background-color: #ffffff; /* Darker green on hover */
            color: green; /* White text on hover */
            border: 2px solid #ffffff; /* White border on hover */
        }
        .tooltip {
            visibility: hidden;
            width: 160px;
            background-color: black;
            color: #fff;
            text-align: center;
            border-radius: 6px;
            padding: 5px;
            position: absolute;
            z-index: 1;
            bottom: 125%; /* Position the tooltip above the button */
            left: 50%;
            margin-left: -80px;
            opacity: 0;
            transition: opacity 0.3s;
        }
        .stButton button:hover .tooltip {
            visibility: visible;
            opacity: 1;
        }
        .tooltip::after {
            content: "";
            position: absolute;
            top: 100%; /* Arrow at the bottom of the tooltip */
            left: 50%;
            margin-left: -5px;
            border-width: 5px;
            border-style: solid;
            border-color: black transparent transparent transparent;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Function to render the circular button with hover text
def render_circle_button(key):
    add_custom_css()
    if st.button('🛈',key=key):
        return True
    return False
    #    return True
    #else:
    #    return False


def clean_csv_files(folder_path):
    # Define the pattern for CSV files
    csv_files_pattern = os.path.join(folder_path, '*.csv')
    
    # Use glob to find all CSV files in the folder
    csv_files = glob.glob(csv_files_pattern)
    
    # Delete all CSV files
    for csv_file in csv_files:
        os.remove(csv_file)

def cleanup_uploads_folder(upload_dir: str):
    try:
        for filename in os.listdir(upload_dir):
            file_path = os.path.join(upload_dir, filename)
            if os.path.isfile(file_path):
                os.unlink(file_path)
    except Exception as e:
        logging.error(f"Error cleaning up uploads folder: {str(e)}")

def convert_excel_to_csv(excel_file_path):
    try:
        df = pd.read_excel(excel_file_path)
        csv_file_path = os.path.splitext(excel_file_path)[0] + ".csv"
        df.to_csv(csv_file_path, index=False)
        os.remove(excel_file_path)
        return csv_file_path
    except Exception as e:
        raise ValueError(f"Error converting Excel to CSV: {str(e)}")

async def read_csv(file_path):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, pd.read_csv, file_path)

@st.cache_data
def chat_with_file(prompt, file_path):
    #file_name = get_file_name()
    #last_uploaded_file_path = os.path.join(UPLOAD_DIR, file_name)
    try:
        if file_path is None or not os.path.exists(file_path):
            raise HTTPException(status_code=400, detail=f"No file has been uploaded or downloaded yet {file_path}")
            
        result = chat_with_agent(prompt, file_path)
        
        return {"response": result}

    except ValueError as e:
        return {"error": f"ValueError: {str(e)}"}
    except Exception as e:
        return {"error": str(e)}

@st.cache_data
def chat_with_agent(input_string, file_path):
    try:
        # Assuming file_path is always CSV after conversion
        df = pd.read_csv(file_path)
        agent = create_csv_agent(
            ChatOpenAI(temperature=0, model="gpt-3.5-turbo"),
            file_path,
            verbose=True,
            agent_type=AgentType.OPENAI_FUNCTIONS
        )
        result = agent.invoke(input_string)
        return result['output']
    except ImportError as e:
        raise ValueError("Missing optional dependency 'tabulate'. Use pip or conda to install tabulate.")
    except pd.errors.ParserError as e:
        raise ValueError("Parsing error occurred: " + str(e))
    except Exception as e:
        raise ValueError(f"An error occurred: {str(e)}")

def fetch_file_info():
    try:
        link = fastapi_url + "/get_file_info/"
        response = requests.get(link)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()
        return data
    except Exception as e:
        st.success("Important Update")
        st.warning("This page was reloaded, so you need to run the report again. After running the report, you may close this page.")
        st.stop()
    except requests.RequestException as e:
        st.error(f"Error fetching file info: {e}")
        return None

@st.cache_data
def cache_df(last_uploaded_file_path):
    if 'df' not in st.session_state:
            st.session_state["df"] = pd.read_csv(last_uploaded_file_path)
    try:
        df = st.session_state["df"]
    except Exception as e:
        st.warning("There is some error with data, try to update the session")
    return df



def big_main():
    #st.session_state
    df = cache_df(last_uploaded_file_path)
    df.index = range(1, len(df) + 1)
    file_type = identify_file(df)
    
    
    if file_type == 'Unknown':
        st.warning(f"This is  {file_type} type report,so this is generated report to it")
    else:
        st.success(f"This is  {file_type} type. File is available for visualization.")
        st.dataframe(df,width=2500, use_container_width=False)
    
    #col1, col2 = st.columns([1, 1])
    tab1, tab2 = st.tabs(["Chat","Build a chart"])
    #with col1:
    with tab1:
        st.info("Chat with GPT")
        
        option = st.selectbox(
            "Perhaps one of the following questions will work for you?",
            ("Write some short useful information about my data as business owner",
             "Write top 3 useful dependecy from data that i should know",
             "Can you extract and summarize the most important performance metrics from this data file?"),
            index=None,
            placeholder="Select one of the frequently asked questions?",
            label_visibility="collapsed")
       #
        if option is None:
            input_text = st.text_area(label='Enter your query:', placeholder="Enter your request to start a chat", label_visibility="collapsed")
        else:
            input_text = option
            input_text = st.text_area(value=input_text, label='Enter your query:', placeholder="Type your question or message and press ‘Submit’", label_visibility="collapsed")
       #
        if input_text is not None:
            
            #\\
            if 'chat_clicked' not in st.session_state:
                st.session_state.chat_clicked = False

            def click_button():
                st.session_state.chat_clicked = True

            st.button('Submit', on_click=click_button, key=1)
            #\\\
            if st.session_state.chat_clicked:
                try:
                    if "chat_result" not in st.session_state:
                        #st.session_state["chat_result"] = ''
                        st.session_state["chat_result"] = chat_with_file(input_text, last_uploaded_file_path)
                        #chat_result = st.session_state["chat_result"]
                    else:
                        st.session_state["chat_result"] = chat_with_file(input_text, last_uploaded_file_path)
                        #chat_result = st.session_state["chat_result"]
                    #chat_result = chat_with_file(input_text, last_uploaded_file_path)
                    if "response" in st.session_state["chat_result"]:
                        st.success(st.session_state["chat_result"]["response"])
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
    #with col2:
    with tab2:
        st.info("Build a Chart")
        
        option1 = st.selectbox(
            "Perhaps one of the following questions will work for you?",
            ("Plot some useful chart with interesting data dependencies",
             "Build a distribution of data from the most useful column",
             "Build a visualization for the columns that can show useful dependencies"),
            index=None,
            placeholder="Select one of the frequently asked questions?",
            label_visibility="collapsed",
            key=322)
        
        if option1 is None:
            input_text2 =st.text_area(label = 'Enter your query for the plot', placeholder = "Enter your request to generate a chart", label_visibility="collapsed")
        else:
            input_text2 = option1
            input_text2 =st.text_area(value=input_text2, label = 'Enter your query for the plot', placeholder = "Enter your query to generate a chart and press ‘Submit’", label_visibility="collapsed")
        
        
        if input_text2 is not None:
            #\\
            if 'plot_clicked' not in st.session_state:
                st.session_state.plot_clicked = False

            def click_button():
                st.session_state.plot_clicked = True

            
            st.button('Submit', on_click=click_button, key=2)
            #\\\
            if st.session_state.plot_clicked:
                #st.session_state.click = True
                st.info("Plotting your Query: " + input_text2)
                #result = build_some_chart(df, input_text2)
                try:
                    plot_result = test_plot_maker(df, input_text2)
                    st.plotly_chart(plot_result)
                    #st.success(result)
                except Exception as e:
                    st.warning("There is some error with data visualization, try to make query more details")
    
    
   
    
    
    
    if df.empty:
        st.warning("### This data report is empty - try downloading another one to get better visualizations")
    
    
    
    
    
    elif file_type == "3rd Party Sales Summary report":
        #cc1, cc2 = st.columns([1,1])
        #with cc1:
            columns = get_csv_columns(last_uploaded_file_path)
            third_party_sales_viz.preprocess_data(pd.read_csv(last_uploaded_file_path))
            if "Product name" in columns and "Grand total" in columns:
                with st.container(border=True):
                    col11, col12 = st.columns([10, 0.45])
                    with col11:
                        st.markdown("""
                        <style>
                        .big-font {
                            font-size:20px !important;
                        }</style>""", unsafe_allow_html=True)

                        st.markdown('<p class="big-font">InvTotal Revenue by Product</p>', unsafe_allow_html=True)
                    with col12:
                        if st.button("🛈", key=424, help="Get some plot information", use_container_width=False):
                            #if render_circle_button(22):
                            condition = True
                        else:
                            condition = False

                        # Check the state of the button
                    tab1, tab2 = st.tabs(["Total Sales", "Order Distribution"])
                    with tab1:
                        if condition == True:
                            st.markdown("""
                            This chart shows how total sales are split across product categories over time. See which categories drive sales in each period and spot any trends.
                            """)
                        third_party_sales_viz.visualize_product_analysis1(df)
                    with tab2:
                        if condition == True:
                            st.markdown("""
                            This chart displays the number of orders for each product, indicating their popularity and helping you manage inventory effectively.
                            """)
                        third_party_sales_viz.visualize_product_analysis2(df)
                        
            else:
                st.warning("There is no Grand total or Product name, so visualizing can not be ready")
            
            if "Customer" in columns and "Product name" in columns and "QTY" in columns and "Grand total" in columns:
                with st.container(border=True):
                    col11, col12 = st.columns([10, 0.45])
                    with col11:
                        st.markdown("""
                        <style>
                        .big-font {
                            font-size:20px !important;
                        }</style>""", unsafe_allow_html=True)

                        st.markdown('<p class="big-font">Top 10 Customers by Sales Amount</p>', unsafe_allow_html=True)
                    with col12:
                        if st.button("🛈", key=425, help="Get some plot information", use_container_width=False):
                            #if render_circle_button(22):
                            condition = True
                        else:
                            condition = False

                        # Check the state of the button
                    if condition == True:
                        st.markdown("""
                    ## Top Customer Insights
                    This chart highlights your top 10 customers by sales revenue. Prioritize these key relationships to drive future sales and consider loyalty programs to encourage repeat business.
                    """)
                    third_party_sales_viz.visualize_sales_trends(df)
            else:
                st.warning("There is no Customer or Product name or Quantity or Grand total, so visualizing can not be ready")
            
            if "Product name" in columns and "QTY" in columns and "Grand total" in columns:
                with st.container(border=True):
                    col11, col12 = st.columns([10, 0.45])
                    with col11:
                        st.markdown("""
                        <style>
                        .big-font {
                            font-size:20px !important;
                        }</style>""", unsafe_allow_html=True)

                        st.markdown('<p class="big-font">Dependence between Quantity and Amount (by Product)</p>', unsafe_allow_html=True)
                    with col12:
                        if st.button("🛈", key=426, help="Get some plot information", use_container_width=False):
                            #if render_circle_button(22):
                            condition = True
                        else:
                            condition = False

                        # Check the state of the button
                    if condition == True:
                        st.markdown("""
                        ## Sales by Quantity and Product

                        This chart shows how sales revenue varies with the quantity of products sold, broken down by product name. Analyze which products contribute the most at different quantity levels.
                        """)
                    third_party_sales_viz.visualize_combined_analysis(df)
            else:
                st.warning("There is no Delivery status or Product name or Quantity or Grand total, so visualizing can not be ready")
            
        #with cc2:
            columns = get_csv_columns(last_uploaded_file_path)
            #if "Discount type" in columns and "Total invoice discount" in columns:
            #    third_party_sales_viz.visualize_discount_analysis(df)
            #else:
            #    st.warning("There is no Discount type or Total invoice discount, so visualizing can not be ready")
            # line_chart_plotly()
            if "Discount type" in columns:
                with st.container(border=True):
                    col11, col12 = st.columns([10, 0.45])
                    with col11:
                        st.markdown("""
                        <style>
                        .big-font {
                            font-size:20px !important;
                        }</style>""", unsafe_allow_html=True)

                        st.markdown('<p class="big-font">Dependence between Quantity and Amount (by Product)</p>', unsafe_allow_html=True)
                    with col12:
                        if st.button("🛈", key=427, help="Distribution of Discount Types", use_container_width=False):
                            #if render_circle_button(22):
                            condition = True
                        else:
                            condition = False

                        # Check the state of the button
                    if condition == True:
                        st.markdown("""
                    ## Discount Usage

                    This chart presents the distribution of discount types used in orders. It highlights the proportion of orders associated with each discount category.
                    """)
                    third_party_sales_viz.analyze_discounts(df)
            else:
                st.warning("There is no Discount type, so visualizing can not be ready")
            
            if "Grand total" in columns and "Manufacturer specific discount" in columns and "Customer discount" in columns:
                with st.container(border=True):
                    col11, col12 = st.columns([10, 0.45])
                    with col11:
                        st.markdown("""
                        <style>
                        .big-font {
                            font-size:20px !important;
                        }</style>""", unsafe_allow_html=True)

                        st.markdown('<p class="big-font">Dependence between Quantity and Amount (by Product)</p>', unsafe_allow_html=True)
                    with col12:
                        if st.button("🛈", key=428, help="Sales, Manufacturer, and Customer Discounts Over Time", use_container_width=False):
                            #if render_circle_button(22):
                            condition = True
                        else:
                            condition = False

                        # Check the state of the button
                    if condition == True:
                        st.markdown("""
                    This area chart displays how the grand total, manufacturer discounts, and customer discounts have fluctuated over time. Track how these values change, identifying periods of high discounts and understanding the overall impact of discounts on sales revenue. 
                    """)
                    third_party_sales_viz.area_visualisation(df)
            else:
                st.warning("There is no Grand total or Manufacturer specific discount or Customer discount, so visualizing can not be ready")
    elif file_type == "Order Sales Summary report":
        #cc1, cc2 = st.columns([1,1])
        #with cc1:
            columns = get_csv_columns(last_uploaded_file_path)
            #df = order_sales_summary_viz.preprocess_data(pd.read_csv(last_uploaded_file_path))
            
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

                    tab1, tab2 = st.tabs(["Top Customers", "Monthly Trend"])
                    with tab1:
                        if condition == True:
                            st.markdown("""
                            This chart highlights your top 10 customers by sales amount. Use it to:

                            * **Focus on High-Value Customers:** Prioritize relationships with clients who contribute the most to revenue.
                            * **Evaluate Sales Performance:** Compare sales contributions and identify potential gaps or disparities.
                            * **Segment and Target Effectively:** Group similar customers for targeted marketing and tailored offerings.
                            """)
                        order_sales_summary_viz.visualize_product_analysis1(df)
                    with tab2:
                        if condition == True:
                            st.markdown("""
                            This line chart tracks your overall sales trajectory over time. Use it to:

                            * **Identify Sales Patterns:** Spot trends (increasing/decreasing sales), seasonality, and periods of growth or decline.
                            * **Analyze Monthly Performance:** Investigate months with exceptionally high or low sales to understand contributing factors.
                            * **Improve Sales Forecasting:** Forecast future sales based on observed trends and seasonality.
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

                    tab1, tab2 = st.tabs(["Top Customers", "By Type"])
                    with tab1:
                        if condition == True:
                            st.markdown("""
                            This pie chart shows the proportion of total discounts by type. It helps to:

                            - **Evaluate Discount Strategy:** Identify which discount types are most impactful.
                            - **Compare Discount Options:** Spot areas for optimization or experimentation.
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
            
        #with cc2:
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
            
            # line_chart_plotly()
        # todo check map data  (addresses or coordinates)
        #map_features()
        #pycdeck_map()
    elif file_type == "Best Sellers report":
        #cc1, cc2 = st.columns([1,1])
        #with cc1:
            columns = get_csv_columns(last_uploaded_file_path)
            df = best_sellers_viz.preprocess_data(pd.read_csv(last_uploaded_file_path))
            
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
            
        #with cc2:
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

                        # Check the state of the button
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
    elif file_type == "Representative Details report":
        #cc1, cc2 = st.columns([1,1])
        #with cc1:
            columns = get_csv_columns(last_uploaded_file_path)
            df = reps_details_viz.preprocess_data(pd.read_csv(last_uploaded_file_path))
            
            if "Total working hours" in columns and "Total visits" in columns and "Assigned customers" in columns and "Role"in columns:
                with st.container(border=True):
                    col11, col12 = st.columns([10, 0.45])
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
                    col11, col12 = st.columns([10, 0.45])
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
                    col11, col12 = st.columns([10, 0.45])
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
                        ## Travel Efficiency: Distance vs. Visits

                        This scatter plot shows the relationship between total travel distance and the number of visits. Each point represents a team member, colored by their role.

                        Use this plot to identify trends, outliers, and opportunities to optimize travel routes.
                        """)
                    reps_details_viz.plot_travel_efficiency_line(df)
            else:
                st.warning("There is no Total travel distance or Total visits or Role columns, so visualizing can not be ready")
            
        #with cc2:
            if "Total working hours" in columns and "Total break hours" in columns and "Total travel distance" in columns:
                with st.container(border=True):
                    col11, col12 = st.columns([10, 0.45])
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
                    col11, col12 = st.columns([10, 0.45])
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
                        ## Visits vs. Photos: Exploring the Relationship

                        These scatter plots analyze the relationship between total visits and the number of photos taken by team members for each role. This visualization helps to understand engagement levels and photo-taking patterns.
                        """)
                    reps_details_viz.plot_visits_vs_photos_separate(df)
            else:
                st.warning("There is no Role or Total visits or Total photos columns, so visualizing can not be ready")
            
            if "Role" in columns and "Assigned customers" in columns:
                with st.container(border=True):
                    col11, col12 = st.columns([10, 0.45])
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
    elif file_type == "Reps Summary report":
        #cc1, cc2 = st.columns([1,1])
        #with cc1:
            columns = get_csv_columns(last_uploaded_file_path)
            df = reps_summary_viz.preprocess_data(pd.read_csv(last_uploaded_file_path))
            
            if "Orders" in columns and "Total revenue" in columns and "Cases sold" in columns:
                with st.container(border=True):
                    col11, col12 = st.columns([10, 0.45])
                    with col11:
                        st.markdown("""
                        <style>
                        .big-font {
                            font-size:20px !important;
                        }</style>""", unsafe_allow_html=True)

                        st.markdown('<p class="big-font">Revenue Drivers: Orders and Cases Sold</p>', unsafe_allow_html=True)
                    with col12:
                        if st.button("🛈", key=471, help="Get some plot information", use_container_width=False):
                            #if render_circle_button(22):
                            condition = True
                        else:
                            condition = False

                    tab1, tab2 = st.tabs(["Orders vs. Revenue", "Cases Sold vs. Revenue"])
                    with tab1:
                        if condition == True:
                            st.markdown("""
                        These scatter plots analyze the relationships between revenue, orders placed, and cases sold. Explore these visualizations to identify key revenue drivers and understand how order volume and sales volume individually influence your bottom line. This can guide your sales strategies for maximizing revenue growth.
                        """)
                        reps_summary_viz.plot_sales_relationships1(df)
                    with tab2:
                        if condition == True:
                            st.markdown("""
                        These scatter plots analyze the relationships between revenue, orders placed, and cases sold. Explore these visualizations to identify key revenue drivers and understand how order volume and sales volume individually influence your bottom line. This can guide your sales strategies for maximizing revenue growth.
                        """)
                        reps_summary_viz.plot_sales_relationships2(df)
            else:
                st.warning("There is no Orders or Total revenue or Cases sold columns, so visualizing can not be ready")
            
            if "Date" in columns and "Role" in columns and "Total revenue" in columns:
                with st.container(border=True):
                    col11, col12 = st.columns([10, 0.45])
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
                    col11, col12 = st.columns([10, 0.45])
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
                    col11, col12 = st.columns([10, 0.45])
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
            
        #with cc2:
            if "Name" in columns and "Visits" in columns and "Travel distance" in columns:
                with st.container(border=True):
                    col11, col12 = st.columns([10, 0.45])
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
            
            if "Visits" in columns and "Orders" in columns:
                with st.container(border=True):
                    col11, col12 = st.columns([10, 0.45])
                    with col11:
                        st.markdown("""
                        <style>
                        .big-font {
                            font-size:20px !important;
                        }</style>""", unsafe_allow_html=True)

                        st.markdown('<p class="big-font">Visits vs. Orders: Exploring the Relationship</p>', unsafe_allow_html=True)
                    with col12:
                        if st.button("🛈", key=469, help="Get some plot information", use_container_width=False):
                            #if render_circle_button(22):
                            condition = True
                        else:
                            condition = False

                        # Check the state of the button
                    if condition == True:
                        st.markdown("""
                        This scatter plot, enhanced with a regression line, visualizes the relationship between the number of visits made by sales representatives and the number of orders generated. Analyze this visualization to understand the correlation between visits and orders, identify potential outliers, and gain insights into the effectiveness of sales efforts.

                        The trendline represents the best-fit linear relationship between visits and orders. The R² value indicates how well the trendline fits the data, with values closer to 1 suggesting a stronger relationship.
                        """)
                    reps_summary_viz.plot_orders_vs_visits_with_regression(df)
            else:
                st.warning("There is no Visits or Orders columns, so visualizing can not be ready")
            
            if "Role" in columns and "Visits" in columns and "Orders" in columns and "Cases sold" in columns:
                with st.container(border=True):
                    col11, col12 = st.columns([10, 0.45])
                    with col11:
                        st.markdown("""
                        <style>
                        .big-font {
                            font-size:20px !important;
                        }</style>""", unsafe_allow_html=True)

                        st.markdown('<p class="big-font">Performance Metrics by Role</p>', unsafe_allow_html=True)
                    with col12:
                        if st.button("🛈", key=470, help="Get some plot information", use_container_width=False):
                            #if render_circle_button(22):
                            condition = True
                        else:
                            condition = False

                        # Check the state of the button
                    if condition == True:
                        st.markdown("""
                        This bar chart provides a comparative overview of key performance metrics (visits, orders, and cases sold) across different sales roles. Analyzing these metrics together can help you identify which roles are excelling in specific areas and pinpoint opportunities for improvement. 
                        """)
                    reps_summary_viz.plot_multiple_metrics_by_role(df)
            else:
                st.warning("There is no Role or Visits or Orders or Cases sold columns, so visualizing can not be ready")
            
            if "Cases sold" in columns and "Total revenue" in columns and "Visits" in columns and "Travel distance" in columns:
                with st.container(border=True):
                    col11, col12 = st.columns([10, 0.45])
                    with col11:
                        st.markdown("""
                        <style>
                        .big-font {
                            font-size:20px !important;
                        }</style>""", unsafe_allow_html=True)

                        st.markdown('<p class="big-font">Revenue vs. Cases Sold: Insights from Visits and Travel</p>', unsafe_allow_html=True)
                    with col12:
                        if st.button("🛈", key=1471, help="Get some plot information", use_container_width=False):
                            #if render_circle_button(22):
                            condition = True
                        else:
                            condition = False

                        # Check the state of the button
                    if condition == True:
                        st.markdown("""
                        This interactive scatter plot provides a comprehensive view of your sales data. Explore the relationship between revenue and cases sold, with the size of each point representing visit frequency and color indicating travel distance. This visualization allows you to uncover deeper insights into the factors influencing sales performance and identify potential areas for optimization.  
                        """)
                    reps_summary_viz.plot_revenue_vs_cases_sold_with_size_and_color(df)
            else:
                st.warning("There is no Cases sold or Total revenue or Visits or Travel distance columns, so visualizing can not be ready")
    elif file_type == "SKU's Not Ordered report":
        #cc1, cc2 = st.columns([1,1])
        #with cc1:
            columns = get_csv_columns(last_uploaded_file_path)
            df = skus_not_ordered_viz.preprocess_data(pd.read_csv(last_uploaded_file_path))
            
            if "Category name" in columns:
                with st.container(border=True):
                    col11, col12 = st.columns([10, 0.45])
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
            else:
                st.warning("There is no Category name column, so visualizing can not be ready")
            
            if "Available cases (QTY)" in columns:
                with st.container(border=True):
                    col11, col12 = st.columns([10, 0.45])
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
            else:
                st.warning("There is no Available cases (QTY) column, so visualizing can not be ready")
            
            if "Category name" in columns and "Retail price" in columns and "Available cases (QTY)" in columns:
                with st.container(border=True):
                    col11, col12 = st.columns([10, 0.45])
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
            else:
                st.warning("There is no Category name or Retail price or Available cases (QTY) columns, so visualizing can not be ready")
            
        #with cc2:
            if "Available cases (QTY)" in columns and "Retail price" in columns and "Wholesale price" in columns and "Category name" in columns:
                with st.container(border=True):
                    col11, col12 = st.columns([10, 0.45])
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
            else:
                st.warning("There is no Available cases (QTY) or Retail price or Wholesale price columns, so visualizing can not be ready")
            
            if "Category name" in columns and "Retail price" in columns:
                with st.container(border=True):
                    col11, col12 = st.columns([10, 0.45])
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
            else:
                st.warning("There is no Category name or Retail price columns, so visualizing can not be ready")
    elif file_type == "Low Stock Inventory report":
        #cc1, cc2 = st.columns([1,1])
        #with cc1:
            columns = get_csv_columns(last_uploaded_file_path)
            df = low_stock_inventory_viz.preprocess_data(pd.read_csv(last_uploaded_file_path))
            
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

                    tab1, tab2 = st.tabs(["Distribution by Category", "Price vs. Quantity"])
                    with tab1:
                        if condition == True:
                            st.markdown("""
                            ## Low Stock Insights: A Deeper Dive

                            This analysis focuses on products with low stock levels. The first chart breaks down these items by category, allowing you to quickly pinpoint areas of concern. The second chart visualizes the relationship between wholesale price and available quantity, offering a more granular perspective on inventory levels for each product.  
                            """)
                        low_stock_inventory_viz.low_stock_analysis_app1(df)
                    with tab2:
                        if condition == True:
                            st.markdown("""
                            ## Low Stock Insights: A Deeper Dive

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
            
        #with cc2:
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
                        ## Quantity/Price Ratio: A Closer Look at Low Stock

                        This horizontal bar chart visualizes the ratio of available quantity to retail price for each low-stock item. Products with higher ratios might indicate overstocking or potential pricing issues, while those with lower ratios could signal high demand or potential stock shortages.
                        """)
                    low_stock_inventory_viz.create_quantity_price_ratio_plot(df)
            else:
                st.warning("There is no Available cases (QTY) or Retail price columns, so visualizing can not be ready")
    elif file_type == "Current Inventory report":
        #cc1, cc2 = st.columns([1,1])
        #with cc1:
            columns = get_csv_columns(last_uploaded_file_path)
            df = current_inventory_viz.preprocess_data(pd.read_csv(last_uploaded_file_path))

            if "Available cases (QTY)" in columns and "Wholesale price" in columns and "Category name" in columns:
                
                with st.container(border=True):
                    col11, col12 = st.columns([10, 0.45])
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
                        ## Inventory Value: A Category Breakdown    
                        This bar chart illustrates the proportional distribution of inventory value across different product categories, allowing you to quickly see which categories hold the most significant value within your inventory.
                        """)
                    current_inventory_viz.df_analyze_inventory_value_by_category(df)
            else:
                st.warning("There is no Available cases (QTY) or Wholesale price columns, so visualizing can not be ready")
            
            if "Available cases (QTY)" in columns and "Retail price" in columns and "Category name" in columns and "Wholesale price" in columns:
                with st.container(border=True):
                    col11, col12 = st.columns([10, 0.45])#([1, 1.705])
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
                        ## Quantity, Price, and Category: A Multi-Factor View

                        This scatter plot provides a visual analysis of the interplay between available quantity, retail price, category, and wholesale price. Explore how these factors relate to each other, uncover potential trends within categories, and identify outliers that might require further investigation. Use these insights to inform your pricing, inventory, and product strategies. 
                        """)
                    current_inventory_viz.df_analyze_quantity_vs_retail_price(df)
                    
            else:
                st.warning("There is no Available cases (QTY) or Retail price or Category name columns, so visualizing can not be ready")
            
            if "Available cases (QTY)" in columns and "Wholesale price" in columns and "Manufacturer name" in columns:
                with st.container(border=True):
                    col11, col12 = st.columns([10, 0.45])#([1, 1.95])
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
                        ## Inventory Value: A Manufacturer Breakdown
                        This bar chart illustrates the proportional distribution of inventory value across different manufacturers. This allows you to see at a glance which manufacturers contribute the most to your overall inventory value. 
                        """)
                    current_inventory_viz.df_analyze_inventory_value_by_manufacturer(df)
                
                
            else:
                st.warning("There is no Available cases (QTY) or Manufacturer name or Wholesale price columns, so visualizing can not be ready")
            
        #with cc2:
            if "Wholesale price" in columns and "Available cases (QTY)" in columns and "Product name" in columns:
                with st.container(border=True):
                    col11, col12 = st.columns([10, 0.45])#([1, 2.35])
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
                    col11, col12 = st.columns([10, 0.45])#([1, 2])
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
    elif file_type == "Top Customers report":
        #cc1, cc2 = st.columns([1,1])
        #with cc1:
            columns = get_csv_columns(last_uploaded_file_path)
            df = top_customers_viz.preprocess_data(pd.read_csv(last_uploaded_file_path))
            if "Name" in columns and "Total sales" in columns and "Territory" in columns and "Payment terms" in columns:
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
                        if st.button("🛈", key=505, help="Customer Sales Analysis", use_container_width=False):
                            #if render_circle_button(22):
                            condition = True
                        else:
                            condition = False

                    tab1, tab2, tab3 = st.tabs(["Top Customers", "Territory Analysis", "Payment Terms Analysis"])
                    with tab1:
                        if condition == True:
                            st.markdown("""
                            This dashboard provides an overview of customer sales patterns, focusing on your top-performing customers, sales distribution across different territories, and a breakdown of sales by payment terms. Use this information to identify key customer segments, optimize sales strategies, and improve cash flow management.
                            """)
                        top_customers_viz.customer_analysis_app1(df)
                    with tab2:
                        if condition == True:
                            st.markdown("""
                            This dashboard provides an overview of customer sales patterns, focusing on your top-performing customers, sales distribution across different territories, and a breakdown of sales by payment terms. Use this information to identify key customer segments, optimize sales strategies, and improve cash flow management.
                            """)
                        top_customers_viz.customer_analysis_app2(df)
                    with tab3:
                        if condition == True:
                            st.markdown("""
                            This dashboard provides an overview of customer sales patterns, focusing on your top-performing customers, sales distribution across different territories, and a breakdown of sales by payment terms. Use this information to identify key customer segments, optimize sales strategies, and improve cash flow management.
                            """)
                        top_customers_viz.customer_analysis_app3(df)
            else:
                st.warning("There is no Name or Total sales or Territory or Payment terms columns, so visualizing can not be ready")
            
            if "Payment terms" in columns:
                with st.container(border=True):
                    col11, col12 = st.columns([10, 0.45])
                    with col11:
                        st.markdown("""
                        <style>
                        .big-font {
                            font-size:20px !important;
                        }</style>""", unsafe_allow_html=True)

                        st.markdown('<p class="big-font">Distribution by every columns</p>', unsafe_allow_html=True)
                    with col12:
                        if st.button("🛈", key=506, help="Get some plot information", use_container_width=False):
                            #if render_circle_button(22):
                            condition = True
                        else:
                            condition = False

                        # Check the state of the button
                    if condition == True:
                        st.markdown("""Useful to see data distribution of all columns
                        """)
                    top_customers_viz.interactive_bar_plot_app(df)
            else:
                st.warning("There is no Payment terms column, so visualizing can not be ready")
            
        #with cc2:
            if "Total sales" in columns:
                with st.container(border=True):
                    col11, col12 = st.columns([10, 0.45])
                    with col11:
                        st.markdown("""
                        <style>
                        .big-font {
                            font-size:20px !important;
                        }</style>""", unsafe_allow_html=True)

                        st.markdown('<p class="big-font">Distribution of Non-Zero Total Sales</p>', unsafe_allow_html=True)
                    with col12:
                        if st.button("🛈", key=507, help="Get some plot information", use_container_width=False):
                            #if render_circle_button(22):
                            condition = True
                        else:
                            condition = False

                        # Check the state of the button
                    if condition == True:
                        st.markdown("""
                    This line chart illustrates the distribution of non-zero total sales values, providing a visual representation of sales frequencies. Analyze the shape of the line to identify common sales value ranges, potential outliers (sudden spikes or drops), and gain a better understanding of the overall sales distribution.
                    """)
                    top_customers_viz.create_non_zero_sales_grouped_plot(df)
            else:
                st.warning("There is no Total sales column, so visualizing can not be ready")
            
            if "Group" in columns and "Billing city" in columns:
                with st.container(border=True):
                    col11, col12 = st.columns([10, 0.45])
                    with col11:
                        st.markdown("""
                        <style>
                        .big-font {
                            font-size:20px !important;
                        }</style>""", unsafe_allow_html=True)

                        st.markdown('<p class="big-font">Customer Group Distribution</p>', unsafe_allow_html=True)
                    with col12:
                        if st.button("🛈", key=508, help="Get some plot information", use_container_width=False):
                            #if render_circle_button(22):
                            condition = True
                        else:
                            condition = False

                        # Check the state of the button
                    if condition == True:
                        st.markdown("""
                    ## Geographic Insights: Customer Group Distribution

                    This interactive visualization explores the distribution of customer groups across different cities. Analyze how customer groups are concentrated or spread out geographically, identify key markets, and uncover potential opportunities for expansion or targeted marketing efforts. 
                    """)
                    top_customers_viz.interactive_group_distribution_app(df)
            else:
                st.warning("There is no Group or Billing city columns, so visualizing can not be ready")
    elif file_type == "Customer Details report":
        #cc1, cc2 = st.columns([1,1])
        #with cc1:
            columns = get_csv_columns(last_uploaded_file_path)
            df = customer_details_viz.preprocess_data(pd.read_csv(last_uploaded_file_path))
            
            if "Group" in columns and "Total orders" in columns and "Total sales" in columns:
                with st.container(border=True):
                    col11, col12 = st.columns([10, 0.45])
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
                    col11, col12 = st.columns([10, 0.45])
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
            
        #with cc2:
            if "Total sales" in columns:
                with st.container(border=True):
                    col11, col12 = st.columns([10, 0.45])
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
                        ## Sales Value Distribution: Insights for Growth

                        This visualization reveals how non-zero total sales values are distributed. Use these insights to refine your pricing and promotion strategies, enhance sales forecasting, optimize product development, and effectively manage potential risks.
                        """)
                    customer_details_viz.create_interactive_non_zero_sales_plot(df)
            else:
                st.warning("There is no Total sales column, so visualizing can not be ready")
            
                
            if "Total sales" in columns and "Group" in columns and "Billing state" in columns:
                with st.container(border=True):
                    col11, col12 = st.columns([10, 0.45])
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
    else:
        df = customer_details_viz.preprocess_data(pd.read_csv(last_uploaded_file_path))
        
        try:
            st.write(big_summary(last_uploaded_file_path))
        except Exception as e:
            st.warning("There is some error with data summary, try to update the session")

        try:
            summary_lida(df)
        except Exception as e:
            st.warning("There is some error with custom data visualization, try to update the session")
        
        




async def main_viz():
    global last_uploaded_file_path

    try:
        if "result" not in st.session_state:
            st.session_state["result"] = fetch_file_info()

        result = st.session_state["result"]
    except Exception as e:
        st.success("Important Update")
        st.warning("This page was reloaded, so you need to run the report again. After running the report, you may close this page.")
    
    if "url" not in st.session_state:
        if "file_name" not in st.session_state:
            st.session_state["url"] = result.get("url")
            st.session_state["file_name"] = result.get("file_name")

    if "clean" not in st.session_state:
        st.session_state["clean"] = True
        cleanup_uploads_folder(UPLOAD_DIR)
        
    url_name = st.session_state["url"]
    file_name_ = st.session_state["file_name"]


    filename = get_file_name()
    #if "last_uploaded_file_path" not in st.session_state:
    #     st.session_state["last_uploaded_file_path"] = os.path.join(UPLOAD_DIR, filename)
         
    last_uploaded_file_path = os.path.join(UPLOAD_DIR, filename)
    
    report_type_filenames = {
        'CUSTOMER_DETAILS': 'customer_details.xlsx',
        'TOP_CUSTOMERS': 'top_customers.xlsx',
        'ORDER_SALES_SUMMARY': 'order_sales_summary.xlsx',
        'THIRD_PARTY_SALES_SUMMARY': 'third_party_sales_summary.xlsx',
        'CURRENT_INVENTORY': 'current_inventory.xlsx',
        'LOW_STOCK_INVENTORY': 'low_stock_inventory.xlsx',
        'BEST_SELLERS': 'best_sellers.xlsx',
        'SKU_NOT_ORDERED': 'sku_not_ordered.xlsx',
        'REP_DETAILS': 'rep_details.xlsx',
        'REPS_SUMMARY': 'reps_summary.xlsx',
    }
    response = requests.get(url_name, stream=True)
    response.raise_for_status()
    friendly_filename = report_type_filenames.get(file_name_, 'unknown.xlsx')
    excel_file_path = os.path.join(UPLOAD_DIR, friendly_filename)
    
    with open(excel_file_path, "wb") as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)
    
    excel_files_pattern = os.path.join(UPLOAD_DIR, '*.xls*')
    
    # Use glob to find all Excel files in the folder
    excel_files = glob.glob(excel_files_pattern)
    
    
    
    if excel_files:
        #clean_csv_files(UPLOAD_DIR)
        for excel_file in excel_files:
            try:
                convert_excel_to_csv(excel_file)
            except Exception as e:
                st.warning("Oops, something went wrong. Please try updating the page.")
    
    st.title("Report Analysis")
    #add_custom_css()
    if os.path.exists(last_uploaded_file_path):
        big_main()
    else:
        st.rerun() # TODO: danger zone for reruning
        if os.path.exists(last_uploaded_file_path):
            # Check if there are any Excel files
            big_main()
        else:
            st.warning("Try refreshing the page to get the visualization, if not, try uploading the file again")


def big_summary(file_path):
    try:
        prompt = f"""
        I have a CSV file that contains important business data.
        I need a comprehensive and easy-to-read summary of this data that would be useful for a business owner.
        The summary should include key insights, trends, and any significant patterns or anomalies found in the data.
        Please ensure the summary is concise and written in layman's terms, focusing on actionable insights
        that can help in decision-making.
        """
        result = chat_with_agent(prompt, file_path)
        
        return result

    except ValueError as e:
        return {"error": f"ValueError: {str(e)}"}
    except Exception as e:
        return {"error": str(e)}

def test_plot_maker(df, text):
    from lida import Manager, TextGenerationConfig, llm
    from lida.datamodel import Goal
    lida = Manager(text_gen = llm("openai")) 

    visualization_libraries = "plotly"
    i = 0

    goals = [text]

    textgen_config = TextGenerationConfig(n=1, 
                                      temperature=0.1, model="gpt-4o", 
                                      use_cache=True)

    summary = lida.summarize(df, 
                summary_method="default", textgen_config=textgen_config) 
    textgen_config = TextGenerationConfig(n=1, temperature=0.1, model="gpt-4o", use_cache=True)
    visualizations = lida.visualize(summary=summary, goal=goals[0], textgen_config=textgen_config, library=visualization_libraries)
    if visualizations:  # Check if the visualizations list is not empty
        selected_viz = visualizations[0]
        exec_globals = {'data': df}
        exec(selected_viz.code, exec_globals)
        return exec_globals['chart']
    else:
        st.warning("No visualizations were generated for this query.")    

def summary_lida(df):
    from lida import Manager, TextGenerationConfig, llm
    from lida.datamodel import Goal
    lida = Manager(text_gen = llm("openai")) 
    textgen_config = TextGenerationConfig(n=1, 
                                      temperature=0.1, model="gpt-3.5-turbo-0301", 
                                      use_cache=True)
    # load csv datset
    summary = lida.summarize(df, 
                summary_method="default", textgen_config=textgen_config)     

    goals = lida.goals(summary, n=6, textgen_config=textgen_config)
    visualization_libraries = "plotly"

    cc1, cc2 = st.columns([1,1])
    num_visualizations = 2

    i = 0
    for i, goal in enumerate(goals):
        if i < 3:
            with cc1:
                st.write("The question for the report was generated by artificial intelligence: " + goals[i].question)
                textgen_config = TextGenerationConfig(n=num_visualizations, temperature=0.1, model="gpt-3.5-turbo-0301", use_cache=True)
                visualizations = lida.visualize(summary=summary,goal=goals[i],textgen_config=textgen_config,library=visualization_libraries)
                if visualizations:  # Check if the visualizations list is not empty
                    selected_viz = visualizations[0]
                    exec_globals = {'data': df}
                    exec(selected_viz.code, exec_globals)
                    st.plotly_chart(exec_globals['chart'])
                else:
                    st.write("No visualizations were generated for this goal.")
                
                st.write("### Explanation of why this question can be useful: " + goals[i].rationale)
                st.write("Method of visualization: " + goals[i].visualization)
        else:
            with cc2:
                st.write("The question for the report was generated by artificial intelligence: " + goals[i].question)
                
                textgen_config = TextGenerationConfig(n=num_visualizations, temperature=0.1, model="gpt-3.5-turbo-0301", use_cache=True)
                visualizations = lida.visualize(summary=summary,goal=goals[i],textgen_config=textgen_config,library=visualization_libraries)
                
                if visualizations:  # Check if the visualizations list is not empty
                    selected_viz = visualizations[0]
                    exec_globals = {'data': df}
                    exec(selected_viz.code, exec_globals)
                    st.plotly_chart(exec_globals['chart'])
                else:
                    st.write("No visualizations were generated for this goal.")
                
                st.write("### Explanation of why this question can be useful: " + goals[i].rationale)
                st.write("Method of visualization: " + goals[i].visualization)


if __name__ == "__main__":
    asyncio.run(main_viz())