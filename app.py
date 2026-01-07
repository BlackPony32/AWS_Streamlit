import streamlit as st
from streamlit_extras.stylable_container import stylable_container
import pandas as pd
import os
import openai
import time
import logging
import asyncio
import json
from dotenv import load_dotenv
import httpx
from fastapi import HTTPException, Response
import requests
import glob

from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor
from langchain_experimental.agents.agent_toolkits import create_csv_agent
from langchain.agents.agent_types import AgentType


from reports_type import (best_sellers, current_inventory, customer_details, low_stock_inventory,
                          order_sales_summary, rep_details, reps_summary, sku_not_ordered,
                          third_party_sales_summary, top_customers, inventory_depletion, reps_visits,product_fulfillment)

from side_func import identify_file, identify_file_mini

EXPECTED_COLUMNS = {
    "PRODUCT_FULFILLMENT": [
        "Order ID", "Customer", "Shipping Address", "Shipping City", "Shipping State",
        "Shipping ZIP", "Delivery Status", "Type", "VIA", "Fulfilled By", "Tracking ID",
        "Fulfill Date", "Product Name", "QTY", "Product Price", "Product Total",
        "Payment Status", "Grand Total", "Paid", "Balance", "Contact Phone", "Contact Name"
    ],
    "REPS_VISITS": [
        "Role", "ID", "Name", "Date", "Business Name", "Billing Address", "Billing City",
        "Billing State", "Billing ZIP", "Shipping Address", "Shipping City", "Shipping State",
        "Shipping ZIP", "Check In", "Check Out", "Total Time", "Check In Status",
        "Cases Sold (Direct)", "Cases Sold (3rd party)", "Cases Sold Total", "Notes",
        "Orders (Direct)", "Orders (3rd party)", "Orders Total", "Photos", "Forms Submission"
    ],
    "INVENTORY_DEPLETION": [
        "Business Name", "Shipping Address", "Shipping City", "Shipping State",
        "Shipping ZIP", "Billing Address", "Billing City", "Billing State", "Billing ZIP",
        "Ginger Shots / Digestive Aid / 2 fl oz", "Ginger Shots / Immunity Aid / 2 fl oz",
        "Ginger Shots / Immunity Booster / 2 fl oz", "Ginger Shots / Vitamin C / 2 fl oz"
    ],
    "REPS_SUMMARY": [
        "ID", "Name", "Role", "Visits", "Orders (Direct)", "Orders (3rd party)",
        "Orders Total", "Cases Sold (Direct)", "Cases Sold (3rd party)", "Cases Sold Total",
        "Total Revenue (Direct)", "Total Revenue (3rd party)", "Total Revenue", "Photos",
        "Notes", "New Clients", "Date", "Start Day", "End Day", "Break", "Travel Distance",
        "First Visit", "Last Visit", "Total Time"
    ],
    "REP_DETAILS": [
        "ID", "Name", "Role", "Email", "Phone Number", "Total Visits",
        "Total Photos", "Total Notes", "Total Working Hours", "Total Break Hours",
        "Total Travel Distance", "Assigned Customers", "Active Customers", "Inactive Customers"
    ],
    "SKU_NOT_ORDERED": [
        "Category Name", "Product Name", "SKU", "Manufacturer Name", "Cases Sold",
        "Total Revenue", "Wholesale Price", "Retail Price", "Available Cases (QTY)", 'On Hand Cases', 'Cost'
    ],
    "BEST_SELLERS": [
        "Category Name", "Product Name", "SKU", "On Hand Cases", "Allocated Cases",
        "Manufacturer Name", "Cases Sold", "Total Revenue", "Wholesale Price",
        "Retail Price", "Available Cases (QTY)", 'Cost'
    ],
    "LOW_STOCK_INVENTORY": [
        "Category Name", "Product Name", "SKU", "On Hand Cases", "Allocated Cases",
        "Manufacturer Name", "Available Cases (QTY)", "Wholesale Price", "Retail Price",'Total Revenue', 'Cost'
    ],
    "CURRENT_INVENTORY": [
        "Category Name", "Product Name", "SKU", "On Hand Cases", "Allocated Cases",
        "Manufacturer Name", "Available Cases (QTY)", "Wholesale Price", "Retail Price", 'Total Revenue', 'Cost'
    ],
    "THIRD_PARTY_SALES_SUMMARY": [
        "Customer ID", "Customer", "Billing Address", "Slotting", "Billing City",
        "Billing State", "Billing ZIP", "Shipping Address", "Shipping City", "Shipping State",
        "Shipping ZIP", "Order ID", "Created By", "Date Created", "Product Name",
        "Manufacturer Name", "QTY", "Grand Total", "Discount Type", "Item Specific Discount",
        "Manufacturer Specific Discount", "Total Invoice Discount", "Price List",
        "Customer Discount", "Free Cases", "Order Tags", "Representative"
    ],
    "ORDER_SALES_SUMMARY": [
        "Customer ID", "Customer", "Billing Address", "Slotting", "Billing City",
        "Billing State", "Billing ZIP", "Shipping Address", "Shipping City", "Shipping State",
        "Shipping ZIP", "Order ID", "Created By", "Date Created", "Product Name",
        "Product Price", "Product Total", "Manufacturer Name", "QTY", "Discount Type",
        "Item Specific Discount", "Customer Discount", "Manufacturer Specific Discount",
        "Total Invoice Discount", "Price List", "Free Cases", "Balance", "Payment Status",
        "Expected Payment Date", "Grand Total", "Paid", "Delivery Status", "Delivered",
        "Delivery Methods", "Order Note", "Order Status", "Customer Contact",
        "Representative", "Order Tags", 'Payment Methods', 'Fulfill By'
    ],
    "TOP_CUSTOMERS": [
        "Business Name", "Shipping Address", "Shipping City", "Shipping State",
        "Shipping ZIP", "Billing Address", "Billing City", "Billing State", "Billing ZIP",
        "Group", "Territory", "Total Orders", "Total Sales", "Customer Specific Discount",
        "Price List", "Primary Payment Method", "Has Order Direct", "Payment Terms",
        "Contact Name", "Contact Role", "Contact Phone", "Contact Email", "Business Phone",
        "Business Email", "Business Fax", "Website", "Tags", "Licenses & Certifications", 'Lead Status', 'Representatives'
    ],
    "CUSTOMER_DETAILS": [
        "Business Name", "Shipping Address", "Shipping City", "Shipping State",
        "Shipping ZIP", "Billing Address", "Billing City", "Billing State", "Billing ZIP",
        "Group", "Territory", "Total Orders", "Total Sales", "Customer Specific Discount",
        "Price List", "Primary Payment Method", "Has Order Direct", "Payment Terms",
        "Contact Name", "Contact Role", "Contact Phone", "Contact Email", "Business Phone",
        "Business Email", "Business Fax", "Website", "Tags", "Licenses & Certifications", 'Lead Status', 'Representatives'
    ]
}
import pandas as pd
import logging
from typing import Dict, List


def check_report(file_path: str, report_type: str, url_name) -> Dict:
    """
    Validate a report file against expected columns for a given report type.
    
    Returns:
        Dictionary with validation results:
        {
            'report_type': str,
            'is_valid': bool,
            'missing_columns': List[str],
            'extra_columns': List[str],
            'column_count_match': bool,
            'error': Optional[str]
        }
    """
    result = {
        'report_type': report_type,
        'is_valid': False,
        'missing_columns': [],
        'extra_columns': [],
        'column_count_match': False,
        'error': None
    }

    try:
        #for stage file check
        #logging.info(f'File report link:  {url_name}')
        # Validate report type first
        expected = EXPECTED_COLUMNS.get(report_type)
        if not expected:
            raise ValueError(f"Invalid report type: {report_type}. "
                             f"Valid types: {list(EXPECTED_COLUMNS.keys())}")

        # Read CSV
        df = pd.read_csv(file_path)
        actual_columns = df.columns.tolist()

        # Check columns
        missing = [col for col in expected if col not in actual_columns]
        extra = [col for col in actual_columns if col not in expected]
        
        # Additional validation: column count match
        count_match = len(actual_columns) == len(expected)
        
        # Prepare results
        result.update({
            'is_valid': not missing and not extra,
            'missing_columns': missing,
            'extra_columns': extra,
            'column_count_match': count_match
        })

        # Log discrepancies
        if missing:
            logging.warning(f"[{report_type}] Missing columns: {missing}")
        if extra:
            logging.warning(f"[{report_type}] Extra columns: {extra}")
        if not count_match:
            logging.warning(f"[{report_type}] Column count mismatch. "
                            f"Expected {len(expected)}, found {len(actual_columns)}")

        return result

    except FileNotFoundError as e:
        error_msg = f"File not found: {file_path}"
        logging.error(f"[{report_type}] {error_msg}")
        result['error'] = error_msg
        return result

    except pd.errors.ParserError as e:
        error_msg = f"CSV parsing error: {str(e)}"
        logging.error(f"[{report_type}] {error_msg}")
        result['error'] = error_msg
        return result

    except ValueError as e:
        error_msg = str(e)
        logging.error(f"[{report_type}] {error_msg}")
        result['error'] = error_msg
        return result

    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logging.error(f"[{report_type}] {error_msg}")
        result['error'] = error_msg
        return result

load_dotenv()

fastapi_url = os.getenv('FASTAPI_URL')
NUMBER_SHOWN_ROWS = 8000
log_file_path = "logging_file.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file_path),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def window_name():

    try:
        #temp_upload = get_upload_file()
        dir_name = st.session_state["user_id"]
        if "dir_name" not in st.session_state:
            st.session_state["dir_name"] = dir_name
        
        
        UPLOAD_DIR = f"uploads\\{st.session_state.dir_name}\\"
        if not os.path.exists(UPLOAD_DIR):
            os.makedirs(UPLOAD_DIR)

        file_type = identify_file(UPLOAD_DIR)
        return file_type
    except Exception:
        pass

if "buffer_1" not in st.session_state:
    st.session_state["buffer_1"] = True
    st.session_state["file_type"] = "SimplyDepo report"
else:
    if "file_type" not in st.session_state:
        st.session_state["file_type"] = "SimplyDepo report"
    else:
        st.session_state["file_type"] = window_name()

file_type1 = st.session_state["file_type"]
    
    
st.set_page_config( page_icon='icon.ico', page_title=file_type1)


css='''
<style>
    section.main > div {max-width:75rem}
    
    
    .stTabs [data-baseweb="tab-highlight"] {
        background-color: #409A65;
    }
    .stTabs [data-baseweb="tab-border"] {
        width: 102.8%;
        left: -16px; 
    }
    
    div[data-baseweb="select"] > div {
    border-color: #409A65;
    font-size: 17px;
}
</style>
'''
st.markdown(css, unsafe_allow_html=True)




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

@st.cache_data(show_spinner=False)
def chat_with_file(prompt, file_path, grand_total_value):
    #file_name = get_file_name()
    #last_uploaded_file_path = os.path.join(UPLOAD_DIR, file_name)
    try:
        if file_path is None or not os.path.exists(file_path):
            raise HTTPException(status_code=400, detail=f"No file has been uploaded or downloaded yet {file_path}")
            
        pre_prompt = f'''Please do not include any tables, graphs, or code imports in your response, 
        just answer to the query and make it attractive: {prompt} ?
        Additional support info - users grand total for ALL customers is {grand_total_value}$ use it instead of count yourself as main answer
        else make count base on unique order id value'''

        result = chat_with_agent(pre_prompt, file_path)
        
        return {"response": result}

    except ValueError as e:
        return {"error": f"ValueError: {str(e)}"}
    except Exception as e:
        return {"error": str(e)}

@st.cache_data(show_spinner=False)
def chat_with_agent(input_string, file_path):
    try:
        # Assuming file_path is always CSV after conversion
        #api_key = os.getenv('Chat_Api') ,openai_api_key=api_key
        agent = create_csv_agent(
            ChatOpenAI(temperature=0, model="gpt-4o"),
            file_path,
            verbose=False,
            agent_type=AgentType.OPENAI_FUNCTIONS
        )
        result = agent.invoke(input_string)
        return result['output']
    except pd.errors.ParserError as e:
        logging.error("CSV parsing error: %s", e)
        raise ValueError("Parsing error occurred: " + str(e))
    except Exception as e:
        logging.error("Unexpected error in chat_with_agent: %s", e)
        raise ValueError(f"An error occurred: {str(e)}")

def fetch_file_info():
    try:
        link = fastapi_url + "/get_file_info/"
        response = requests.get(link)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()
        return data
    except requests.RequestException as e:
        logging.error("Request failed: %s", e)
        st.success("""**Important Notice**
        \nThis page was reloaded due to a manual refresh.\n To proceed, please close this window and run the report again from **Simply Depo**. Avoid refreshing the page to ensure smooth operation and avoid interruptions. Thank you for your cooperation.
        """)
        st.stop()
    except Exception as e:
        logging.error("General error in fetch_file_info: %s", e)
        st.success("""**Important Notice**
        \nThis page was reloaded due to a manual refresh.\n To proceed, please close this window and run the report again from **Simply Depo**. Avoid refreshing the page to ensure smooth operation and avoid interruptions. Thank you for your cooperation.
        """)
        st.stop()


#@st.cache_data(show_spinner=False)
def cache_df(last_uploaded_file_path):
    try:
        if 'df' not in st.session_state:
                df = pd.read_csv(last_uploaded_file_path, low_memory=False)
                #df_limited = df.head(NUMBER_SHOWN_ROWS)
                st.session_state["df"] = df  #df_limited

        df = st.session_state["df"]
    except Exception as e:
        st.warning("There is some error with data, try to update the session")
        st.stop()
    return df

def id_str(value):
    if isinstance(value, (int, float)):
        return f"{value:.0f}"
    elif isinstance(value, str) and value.replace(",", "").isdigit():
        return f"{float(value.replace(',', '')):.0f}"
    else:
        return value

def format_phone_number(phone_number):
    # Convert input to string
    phone_str = str(phone_number)
    
    # Return if it's a special case (e.g., starts with '$')
    if phone_str.startswith('$'):
        return phone_str
        
    # Extract only digits from the string
    digits = ''.join(filter(str.isdigit, phone_str))
    
    # Handle 11-digit numbers (with leading '1' country code)
    if len(digits) == 11 and digits.startswith("1"):
        return f"+{digits[0]} ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
    
    # Handle 10-digit numbers
    elif len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    
    # Handle numeric strings that might be floats
    else:
        try:
            # Convert to float then to int to remove decimals
            num = float(phone_str)
            digits_float = f"{num:.0f}"
            # Check formatted float as 11-digit
            if len(digits_float) == 11 and digits_float.startswith("1"):
                return f"+{digits_float[0]} ({digits_float[1:4]}) {digits_float[4:7]}-{digits_float[7:]}"
            # Check formatted float as 10-digit
            elif len(digits_float) == 10:
                return f"({digits_float[:3]}) {digits_float[3:6]}-{digits_float[6:]}"
        except (ValueError, TypeError):
            pass  # Fall through to return original
        
        # Return original if no valid format matches
        return phone_str

def add_dollar_sign(value):
    try:
        # Only format if value is numeric and doesn't already start with $
        if not str(value).startswith('$'):
            return f"${float(value):.2f}"
        else:
            return value
    except ValueError:
        return value

def big_main():
    #st.write(st.session_state.last_uploaded_file_path)
    df = cache_df(st.session_state.last_uploaded_file_path)
    df.index = range(1, len(df) + 1)
    file_type = identify_file(UPLOAD_DIR)
    
    #session block
    if 'AI_appear' not in st.session_state:
        st.session_state.AI_appear = False
    if 'input_text' not in st.session_state:
        st.session_state.input_text = ''
    if 'input_text_img' not in st.session_state:
        st.session_state.input_text_img = ''
    if 'my_input' not in st.session_state:
        st.session_state.my_input = ''
    if 'my_input_img' not in st.session_state:
        st.session_state.my_input_img = ''
    if 'chat_clicked' not in st.session_state:
        st.session_state.chat_clicked = False
    if 'continue_clicked' not in st.session_state:
        st.session_state.continue_clicked = False
    if 'plot_clicked' not in st.session_state:
        st.session_state.plot_clicked = False
    #keyy = os.getenv('OPENAI_API_KEY')
    #st.write(keyy)
    #st.write(st.session_state["user_id"])
    try:
        # #
        with stylable_container(
            key="custom-table",
            css_styles=["""
            button {
                background-color: #ffffff;
                border: 2px solid #47A06D;
                color: #47A06D;
                padding: 0px;
                text-align: center;
                text-decoration: none;
                border-radius: 0%;
                font-size: 17px;
                margin: 4px 2px;
                border-style: solid;
                width: 50px;
                height: 20px;
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
            """,
            """
            container {
                border: 2px #47A06D;
            }
            """],
            ):
            if file_type == 'Unknown':
                st.warning(f"This is  {file_type} type report,so this is generated report to it")
            else:
                if 'report_name' not in st.session_state:
                    st.session_state["report_name"] = file_type
                if df.empty:
                    st.dataframe(df)
                    st.warning("### This data report is empty - try downloading another one to get better visualizations")
                    st.stop()
                else:
                    #some grand total hand fix count and agent feed
                    # Convert Grand Total to numeric
                    try:
                        data = df.copy()
                        grand_total_col, order_id_col, customer_col='Grand total', 'Order Id', 'Customer'

                        data[grand_total_col] = pd.to_numeric(data[grand_total_col], errors='coerce')
                        data = data.dropna(subset=[grand_total_col])

                        # Step 1: Remove duplicate orders (keep first occurrence per Order ID)
                        unique_orders = data.drop_duplicates(subset=[order_id_col])
    
                        # Step 2: Calculate total sales per customer using de-duplicated data
                        customer_sales = unique_orders.groupby(customer_col)[grand_total_col].sum()
                        grand_total_value = customer_sales #sum(customer_sales)
                        #print(f"${grand_total_value:,.0f}")
                    except Exception as e:
                        grand_total_value = 'There is no information about this, so the answer cannot be calculated'
                        pass
                    
                    column_functions = {
                        'Customer ID': id_str,
                        'ID': id_str,
                        'Order ID': id_str,
                        'Order ID': id_str,
                        'Grand Total': add_dollar_sign,
                        'Cost': add_dollar_sign,
                        'Paid': add_dollar_sign,
                        'Item Specific Discount': add_dollar_sign,
                        'Manufacturer Specific Discount': add_dollar_sign,
                        'Total Invoice Discount': add_dollar_sign,
                        'Customer Discount': add_dollar_sign,
                        'Balance': add_dollar_sign,
                        'Product Price': add_dollar_sign,
                        'Product Total': add_dollar_sign,
                        'Wholesale Price': add_dollar_sign,
                        'Retail Price': add_dollar_sign,
                        'Phone Number': format_phone_number,
                        'Contact Phone': format_phone_number,
                        'Total Sales' : add_dollar_sign,
                        'Shipping ZIP' : id_str,
                        'Shipping Zip' : id_str,
                        'Billing ZIP' : id_str,
                        'Billing Zip' : id_str,
                        'Total Revenue': add_dollar_sign
                    }

                    if file_type == "Representative Details report":
                        df_show = df.copy()
                        df_show  = df_show.head(NUMBER_SHOWN_ROWS)

                        for column, func in column_functions.items():
                            if column in df_show.columns:
                                df_show[column] = df_show[column].apply(func)
                            else:
                                pass
                        try:
                            st.dataframe(df_show, use_container_width=False)
                        except:
                            st.warning("Data display error, try reloading the report")
                    elif file_type == "Customer Details report":
                        df_show = df.copy()
                        df_show  = df_show.head(NUMBER_SHOWN_ROWS)

                        for column, func in column_functions.items():
                            if column in df_show.columns:
                                df_show[column] = df_show[column].apply(func)

                        try:
                            st.dataframe(df_show, use_container_width=False)
                        except:
                            st.warning("Data display error, try reloading the report")
                    elif file_type == "Top Customers report":
                        df_show = df.copy()
                        df_show  = df_show.head(NUMBER_SHOWN_ROWS)

                        for column, func in column_functions.items():
                            if column in df_show.columns:
                                df_show[column] = df_show[column].apply(func)

                        try:
                            st.dataframe(df_show, use_container_width=False)
                        except:
                            st.warning("Data display error, try reloading the report")
                    elif file_type == "Order Sales Summary report":
                        df_show = df.copy()
                        _NUMBER_SHOWN_ROWS = 6000
                        df_show  = df_show.head(_NUMBER_SHOWN_ROWS)

                        for column, func in column_functions.items():
                            if column in df_show.columns:
                                df_show[column] = df_show[column].apply(func)

                        try:
                            st.dataframe(df_show, use_container_width=False)
                        except:
                            st.warning("Data display error, try reloading the report")
                    elif file_type == "SKU's Not Ordered report":
                        df_show = df.copy()
                        df_show  = df_show.head(NUMBER_SHOWN_ROWS)

                        for column, func in column_functions.items():
                            if column in df_show.columns:
                                df_show[column] = df_show[column].apply(func)

                        
                        try:
                            st.dataframe(df_show, use_container_width=False)
                        except:
                            st.warning("Data display error, try reloading the report")
                    elif file_type == "Reps Summary report":
                        df_show = df.copy()
                        df_show  = df_show.head(NUMBER_SHOWN_ROWS)

                        for column, func in column_functions.items():
                            if column in df_show.columns:
                                df_show[column] = df_show[column].apply(func)
                        
                        try:
                            st.dataframe(df_show, use_container_width=False)
                        except:
                            st.warning("Data display error, try reloading the report")
                    elif file_type == "Product fulfillment report":
                        df_show = df.copy()
                        df_show  = df_show.head(NUMBER_SHOWN_ROWS)
                        
                        for column, func in column_functions.items():
                            if column in df_show.columns:
                                df_show[column] = df_show[column].apply(func)
                        try:
                            st.dataframe(df_show, use_container_width=False)
                        except Exception as e:
                            #print(e)
                            st.warning("Data display error, try reloading the report")
                    elif file_type == "Low Stock Inventory report":
                        df_show = df.copy()
                        df_show  = df_show.head(NUMBER_SHOWN_ROWS)
                        
                        for column, func in column_functions.items():
                            if column in df_show.columns:
                                df_show[column] = df_show[column].apply(func)
                        try:
                            st.dataframe(df_show, use_container_width=False)
                        except:
                            st.warning("Data display error, try reloading the report")
                    elif file_type =="Best Sellers report":
                        df_show = df.copy()
                        df_show  = df_show.head(NUMBER_SHOWN_ROWS)
                        
                        for column, func in column_functions.items():
                            if column in df_show.columns:
                                df_show[column] = df_show[column].apply(func)
                        
                        try:
                            st.dataframe(df_show, use_container_width=False)
                        except:
                            st.warning("Data display error, try reloading the report")
                    elif file_type == "3rd Party Sales Summary report":
                        df_show = df.copy()
                        df_show  = df_show.head(NUMBER_SHOWN_ROWS)
                        
                        for column, func in column_functions.items():
                            if column in df_show.columns:
                                df_show[column] = df_show[column].apply(func)
                        
                        try:
                            st.dataframe(df_show, use_container_width=False)
                        except:
                            st.warning("Data display error, try reloading the report")
                    elif file_type == "Current Inventory report":
                        df_show = df.copy()
                        df_show  = df_show.head(NUMBER_SHOWN_ROWS)
                        
                        for column, func in column_functions.items():
                            if column in df_show.columns:
                                df_show[column] = df_show[column].apply(func)
                        
                        try:
                            st.dataframe(df_show, use_container_width=False)
                        except:
                            st.warning("Data display error, try reloading the report")
                    elif file_type == "Inventory Depletion report":
                        df_show = df.copy()
                        df_show  = df_show.head(NUMBER_SHOWN_ROWS)
                        
                        for column, func in column_functions.items():
                            if column in df_show.columns:
                                df_show[column] = df_show[column].apply(func)
                        
                        try:
                            st.dataframe(df_show, use_container_width=False)
                        except:
                            st.warning("Data display error, try reloading the report")
                    elif file_type == "Reps visits report":
                        df_show = df.copy()
                        df_show  = df_show.head(NUMBER_SHOWN_ROWS)
                        
                        for column, func in column_functions.items():
                            if column in df_show.columns:
                                df_show[column] = df_show[column].apply(func)
                        
                        try:
                            st.dataframe(df_show, use_container_width=False)
                        except:
                            st.warning("Data display error, try reloading the report")
                    else:
                        try:
                            st.dataframe(df, use_container_width=False)
                        except:
                            st.warning("Data display error, try reloading the report")
    except Exception as e:
        #st.write(str(e))
        st.warning("Data display error, try reloading the report")

    with stylable_container(
        key="chat-ai",
        css_styles=["""
            button {
                background-color: #47A06D;
                border: 2px solid #47A06D;
                color: #ffffff;
                padding: 0px;
                text-align: center;
                text-decoration: none;
                
                font-size: 17px;
                margin: 4px 2px;
                border-style: solid;
                width: 130px;
                height: 50px;
                line-height: 30px;
                position: relative;
            }""",
            """
            button:hover {
                background-color: #409A65;
                
                color: #ffffff;
            }""",
            """
            button:focus {
                background-color: #409A65;
                color: #ffffff;
                border: 2px #47A06D;
            }
            """,
            """
            container {
                border: 2px #47A06D;
            }
            """],
        ):
        
        def click_AI_Appear():
            st.session_state.AI_appear = True
        
        button_AI_appear = st.button('Analyze with AI', on_click=click_AI_Appear, key=888)
        
        @st.dialog("Analyze Selected Data")
        def AI_info():
            def click_cont_button():
                st.session_state.continue_clicked = True
            st.markdown("""
                <div class="custom-container">
                    <p>By clicking 'Continue', you will be connected to ChatGPT service. All information will be provided directly to the OpenAI server. For more information, read the <a href="https://openai.com/policies/privacy-policy/" target="_blank">OpenAI privacy documents</a>.</p>
                </div>
            """, unsafe_allow_html=True)
            # css for text information inside inform container
            st.markdown("""
            <style>
            .custom-container {
                background-color: #f0f0f0;
                border-radius: 10px;
                padding: 20px;
                text-align: center;
            }
            .custom-container h3 {
                margin-bottom: 20px;
            }
            .custom-container p {
                font-size: 18px;
                margin-bottom: 15px;
            }
        </style>
        """, unsafe_allow_html=True)
            # css for button inside inform container 
            with stylable_container(
                key="custom-button-continue",
                css_styles=["""
                    button {
                        background-color: #409A65;
                        border: 2px solid #47A06D;
                        color: #ffffff;
                        padding: 0px;
                        text-align: center;
                        text-decoration: none;
                        border-radius: 4px;
                        font-size: 17px;
                        margin: 4px 2px;
                        border-style: solid;
                        width: 450px;
                        height: 60px;
                        line-height: 30px;
                        position: relative;
                    }
                    """,
                    """
                    button:hover {
                        background-color: #47A06D;
                        box-shadow: 0 12px 16px 0 rgba(0,0,0,0.14), 0 7px 25px 0 rgba(0,0,0,0.09);
                        color: #ffffff;
                    }"""],
            ):
                button1_clicked = st.button('Continue', on_click=click_cont_button, key="custom-button")
            with stylable_container(
                key="custom-button-decline",
                css_styles=["""
                    button {
                        background-color: #ffffff;
                        border: 2px solid #c3c2d1;
                        color: #c3c2d1;
                        padding: 0px;
                        text-align: center;
                        text-decoration: none;
                        border-radius: 4px;
                        font-size: 17px;
                        margin: 4px 2px;
                        border-style: solid;
                        width: 450px;
                        height: 60px;
                        line-height: 30px;
                        position: relative;
                    }
                    """,
                    """
                    button:hover {
                        background-color: #ffffff;
                        box-shadow: 0 12px 16px 0 rgba(0,0,0,0.14), 0 7px 25px 0 rgba(0,0,0,0.09);
                        color: #000000;
                    }"""],
            ):
                button2_clicked = st.button('Decline', key=31)
            if button1_clicked:
                st.rerun() #close window
            if button2_clicked:
                st.session_state.AI_appear = False
                st.rerun() #close window
        
        
        
        if st.session_state.AI_appear:
            if st.session_state.continue_clicked == False:
                AI_info() 
            else:
                with st.container(border=True):

                    with stylable_container(
                    key="custom-tabs-chat-button",
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
                        tab1, tab2 = st.tabs(["Chat","Visualize"])

                        with tab1:
                            #st.info("Chat with GPT")

                            option = st.selectbox(
                                "Choose a query to analyze your CSV data:",  #label is not visible
                                ("Provide a brief summary of key insights for a business owner",
                                 "Identify the top 3 critical dependencies in the data",
                                 "Summarize the most important performance metrics from this CSV",
                                 "Highlight any significant trends or patterns in the data",
                                 "Generate a concise report of data anomalies or outliers"),
                                index=None,
                                placeholder="Frequently asked questions",
                                label_visibility="collapsed",
                                key="selected_1")

                            def update_text():
                                st.session_state['input_text'] = st.session_state['my_input']

                            if option is None:
                                value = st.text_area("Enter your text here:", height=100, placeholder="Message AI", label_visibility="collapsed", key="uniqy")
                                st.session_state['input_text'] = value
                                input_text = st.session_state['input_text']

                            else:
                                value = st.text_area(value=option, label='Message Ai', placeholder="Message Ai", label_visibility="collapsed", on_change=update_text,key="1100")
                                st.session_state['input_text'] = value
                                option = None
                                input_text = st.session_state['input_text']

                            if input_text is not None:
                                #\\
                                def click_button():
                                    st.session_state.chat_clicked = True



                                with stylable_container(
                                key="custom-Submit1-button",
                                css_styles=["""
                                    button {
                                        background-color: #409A65;
                                        border: 2px solid #47A06D;
                                        color: #ffffff;
                                        padding: 0px;
                                        text-align: center;
                                        text-decoration: none;
                                        border-radius: 4px;
                                        font-size: 17px;
                                        margin: 4px 2px;
                                        border-style: solid;
                                        width: 120px;
                                        height: 35px;
                                        line-height: 30px;
                                        position: relative;
                                    }""",
                                    """
                                    button:hover {
                                        background-color: #409A65;
                                        box-shadow: 0 12px 16px 0 rgba(0,0,0,0.14), 0 2px 12px 0 rgba(0,0,0,0.09);
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
                                    button_Submit1 = st.button('Submit', on_click=click_button, key=1)

                                if st.session_state.chat_clicked == True:
                                        if 'input_text' in st.session_state:
                                            user_prompt = st.session_state['input_text']
                                        st.session_state.chat_clicked = False
                                        try:
                                            with st.spinner(text="Analyzing Your Request..."):
                                                if "chat_result" not in st.session_state:
                                                        st.session_state["chat_result"] = chat_with_file(user_prompt, last_uploaded_file_path, grand_total_value)
                                                        #chat_result = st.session_state["chat_result"]
                                                        #chat_result = chat_with_file(input_text, last_uploaded_file_path)
                                                        if "response" in st.session_state["chat_result"]:
                                                            # Inject custom CSS for answer container
                                                            st.write("""
                                                                <style>
                                                                  div[data-testid="stVerticalBlockBorderWrapper"]:has(
                                                                    >div>div>div[data-testid="element-container"] 
                                                                    .red-frame
                                                                  ) {
                                                                    outline: 2px solid #47A06D;
                                                                    border-radius: 12px; 
                                                                  }
                                                                </style>
                                                                """, unsafe_allow_html=True)
                                                            with st.container(border=True):
                                                                st.write('<span class="red-frame"/>', unsafe_allow_html=True)
                                                                st.write(st.session_state["chat_result"]["response"])
                                                        else:
                                                            st.success("There is some error occurred, try to give more details to your prompt")
                                                else:
                                                    #with st.spinner(text="In progress..."):
                                                        chat_result = chat_with_file(user_prompt, last_uploaded_file_path, grand_total_value)
                                                        st.session_state["chat_result"] = chat_result
                                                        #rr = os.getenv("OPENAI_API_KEY")
                                                        #st.write(rr)
                                                        #st.write(st.session_state["chat_result"])
                                                        #chat_result = chat_with_file(input_text, last_uploaded_file_path)
                                                        if "response" in st.session_state["chat_result"]:
                                                            # Inject custom CSS for answer container
                                                            st.write("""
                                                        <style>
                                                          div[data-testid="stVerticalBlockBorderWrapper"]:has(
                                                            >div>div>div[data-testid="element-container"] 
                                                            .red-frame
                                                          ) {
                                                            outline: 2px solid #47A06D;
                                                            border-radius: 12px; 
                                                          }
                                                        </style>
                                                        """, unsafe_allow_html=True)
                                                            with st.container(border=True):
                                                                st.write('<span class="red-frame"/>', unsafe_allow_html=True)
                                                                st.write(st.session_state["chat_result"]["response"])
                                                        else:
                                                            st.success("There is some error occurred, try to give more details to your prompt")
                                        except Exception as e:
                                            st.warning("There is some error occurred with AI, try again")
                                            st.stop()

                        #with col2:
                        with tab2:
                            #st.info("Build a Chart")

                            option1 = st.selectbox(
                                "Perhaps one of the following questions will work for you?",
                                ("Plot some useful chart with interesting data dependencies",
                                 "Build a distribution of data from the most useful column",
                                 "Build a visualization for the columns that can show useful dependencies"),
                                index=None,
                                placeholder="Frequently asked questions",
                                label_visibility="collapsed",
                                key=322)
                            def update_text_img():
                                st.session_state['input_text_img'] = st.session_state['my_input_img']


                            if option1 is None:
                                value1 = st.text_area("Enter your text here:", height=100, placeholder="Message AI", label_visibility="collapsed", key="uniqy1")
                                st.session_state['input_text_img'] = value1
                                input_text2 = st.session_state['input_text_img']

                            else:
                                value1 = st.text_area(value=option1, label='Message Ai', placeholder="Message Ai", label_visibility="collapsed", on_change=update_text_img,key="1101")
                                st.session_state['input_text_img'] = value1
                                option1 = None
                                input_text2 = st.session_state['input_text_img']
                                
                            if input_text2 is not None:
                                #\\
                                def click_button():
                                    st.session_state.plot_clicked = True


                                with stylable_container(
                                    key="custom-Submit2-button",
                                    css_styles=["""
                                        button {
                                        background-color: #409A65;
                                        border: 2px solid #47A06D;
                                        color: #ffffff;
                                        padding: 0px;
                                        text-align: center;
                                        text-decoration: none;
                                        border-radius: 4px;
                                        font-size: 17px;
                                        margin: 4px 2px;
                                        border-style: solid;
                                        width: 120px;
                                        height: 35px;
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
                                    button_Submit2 = st.button('Submit', on_click=click_button, key=2)

                                if button_Submit2:
                                    #\\\
                                    if st.session_state.plot_clicked:
                                        st.session_state.chat_clicked = False
                                        try:
                                            with st.spinner(text="Analyzing Your Request..."):
                                                st.write("""
                                                    <style>
                                                      div[data-testid="stVerticalBlockBorderWrapper"]:has(
                                                        >div>div>div[data-testid="element-container1"] 
                                                        .red-frame
                                                      ) {
                                                        outline: 2px solid #47A06D;
                                                        border-radius: 12px;
                                                      }
                                                    </style>
                                                    """, unsafe_allow_html=True)
                                                with st.container(border=True):
                                                    try:
                                                        st.write('<span class="red-frame"/>', unsafe_allow_html=True)
                                                        plot_result = test_plot_maker(df, input_text2)
                                                        st.plotly_chart(plot_result)
                                                    except Exception as e:
                                                        st.warning("There is some error with data visualization, try to give query more details")


                                        except Exception as e:
                                            st.warning("There is some error with data visualization, try to make query more details")


    #css for inform button
    with stylable_container(
            key="custom-inform-button",
            css_styles=["""
                button {
                    background-color: #ffffff;
                    border: 1px solid #bfc0c2;
                    color: #bfc0c2;
                    padding: 0px;
                    text-align: center;
                    text-decoration: none;
                    border-radius: 13%;
                    font-size: 17px;
                    margin: 4px 2px;
                    border-style: solid;
                    width: 40px;
                    height: 30px;
                    line-height: 30px;
                    position: relative;
                }""",
                """
                button:hover {
                    background-color: #409A65;
                    box-shadow: 0 12px 16px 0 rgba(0,0,0,0), 0 1px 5px 0 rgba(0,0,0,0);
                    color: #ffffff;
                    border: 2px #47A06D;
                }""",
                """
                button:focus {
                    background-color: #409A65;
                    color: #ffffff;
                    border: 2px #47A06D;
                }
                """],
            ):

        report_function_map = {
            '3rd Party Sales Summary report': third_party_sales_summary.report_func,
            'Order Sales Summary report': order_sales_summary.report_func,
            'Best Sellers report': best_sellers.report_func,
            'Representative Details report': rep_details.report_func,
            'Reps Summary report': reps_summary.report_func,
            "SKU's Not Ordered report": sku_not_ordered.report_func,
            'Low Stock Inventory report': low_stock_inventory.report_func,
            'Current Inventory report': current_inventory.report_func,
            'Top Customers report': top_customers.report_func,
            'Customer Details report': customer_details.report_func,
            'Inventory Depletion report': inventory_depletion.report_func,
            'Reps visits report': reps_visits.report_func,
            'Product fulfillment report': product_fulfillment.report_func
        }
        if file_type in report_function_map:
            try:
                report_function_map[file_type](df)
            except Exception as e:
                st.success("Important technical work is underway, please try again later")
        else:
            st.warning("Your report is not standard, so there are no additional visualizations")






def main_viz():
    global last_uploaded_file_path
    global UPLOAD_DIR
    
    #try:
    #    if st.session_state.result:
    #        st.write(st.session_state.result)
    #except Exception as e:
    #    pass
    async def cleanup_uploads_folder(upload_dir: str):
        try:
            # Pause for 0.5 seconds asynchronously
            await asyncio.sleep(0.3)

            # List all files in the directory
            files = [file for file in os.listdir(upload_dir) if os.path.isfile(os.path.join(upload_dir, file))]

            # If there is more than one file, proceed with cleanup
            if len(files) > 1:
                for filename in files:
                    file_path = os.path.join(upload_dir, filename)
                    os.unlink(file_path)
            # else:
            #    st.info("Only one file found in the folder; no cleanup necessary.")

        except Exception as e:
            logger.error(f"Something went wrong during cleanup: {e}")
            #st.warning(f"Something went wrong during cleanup: {e}")
                #logging.error(f"Error cleaning up uploads folder: {str(e)}")

    try:
        if "result" not in st.session_state:
            try:
                st.session_state["result"] = fetch_file_info()
            except Exception as e:
                st.warnings("Something wrong with data")
                st.stop()
        result = st.session_state["result"]
    except Exception as e:
        st.success("""**Important Notice**
        \nThis page was reloaded due to a manual refresh.\n To proceed, please close this window and run the report again from **Simply Depo**. Avoid refreshing the page to ensure smooth operation and avoid interruptions. Thank you for your cooperation.
        """)
    try:    
        if "url" not in st.session_state:
            if "file_name" not in st.session_state:
                if "user_id" not in st.session_state:
                    st.session_state["user_id"] = result.get("user_id")
                    st.session_state["url"] = result.get("url")
                    st.session_state["file_name"] = result.get("file_name")

    except Exception as e:
        st.success("""**Important Notice**
        \nThis page was reloaded due to a manual refresh.\n To proceed, please close this window and run the report again from **Simply Depo**. Avoid refreshing the page to ensure smooth operation and avoid interruptions. Thank you for your cooperation.
        """)
        st.stop()
        
    url_name = st.session_state["url"]
    file_name_ = st.session_state["file_name"]
    user_id = st.session_state["user_id"]
    
    #filename = get_file_name()
    #st.write(filename)
    UPLOAD_DIR = f"uploads\\{user_id}\\"
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)
    #filename = get_file_name(UPLOAD_DIR)
    if "clean" not in st.session_state:
        st.session_state["clean"] = True
    asyncio.run(cleanup_uploads_folder(UPLOAD_DIR)) #if wanna make one time than add in if state "clean"

    #last_uploaded_file_path = os.path.join(UPLOAD_DIR, filename)

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
        'INVENTORY_DEPLETION': 'inventory_depletion.xlsx',
        'REPS_VISITS': 'reps_visits.xlsx',
        'PRODUCT_FULFILLMENT': 'product_fulfillment.xlsx'
    }
    try:
        response = requests.get(url_name, stream=True)
        response.raise_for_status()
    except Exception as e: #if error with file_link
        st.warning("Something wrong with data. Try to rerun the report.")
        st.stop()

    friendly_filename = report_type_filenames.get(file_name_, 'unknown.xlsx')
    excel_file_path = os.path.join(UPLOAD_DIR, friendly_filename)
    
    #if "file_download" not in st.session_state:
    with open(excel_file_path, "wb") as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)
    #    st.session_state.file_download = True
    
    excel_files_pattern = os.path.join(UPLOAD_DIR, '*.xls*')
    time.sleep(0.3)
    # Use glob to find all Excel files in the folder
    excel_files = glob.glob(excel_files_pattern)

    if excel_files:
        for excel_file in excel_files:
            try:
                if "last_uploaded_file_path" not in st.session_state:
                    st.session_state.last_uploaded_file_path = convert_excel_to_csv(excel_file)
                else:
                    #pass
                    st.session_state.last_uploaded_file_path = convert_excel_to_csv(excel_file)
            except Exception as e:
                st.warning("Oops, something went wrong with data. Please try updating the page.")
                st.stop()
    #st.success(f"This is   type. File is available for visualization.")
    last_uploaded_file_path = st.session_state.last_uploaded_file_path
    report_name_title = identify_file_mini(file_name_)
    st.title(f"Report: {report_name_title}")
    
    if "file_result_check" not in st.session_state:
        st.session_state["file_result_check"] = True
        try:
            result_check = check_report(last_uploaded_file_path, st.session_state["file_name"], url_name)
            logger.info(f"File check: {result_check}")
        except Exception as e:
            pass
    
    if "one_rerun" not in st.session_state:
        st.session_state["one_rerun"] = True
        st.rerun()
    
    big_main()
    

@st.cache_data(show_spinner=False)
def test_plot_maker(df, text):
    from lida import Manager, TextGenerationConfig, llm
    from lida.datamodel import Goal
    lida = Manager(text_gen = llm("openai")) 

    visualization_libraries = "plotly"
    i = 0

    goals = [text]
    #viz_key = os.getenv('Visualizations_Api')   , openai_api_key=viz_key
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
        logger.error(f"AI visualization generate: {visualizations}")
        st.warning("No visualizations were generated for this query.")    


if __name__ == "__main__":
    main_viz()