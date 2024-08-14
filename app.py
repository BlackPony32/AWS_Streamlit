import streamlit as st
from streamlit_extras.stylable_container import stylable_container
import pandas as pd
import os
import openai
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
from reports_type import (best_sellers, current_inventory, customer_details, low_stock_inventory,
                          order_sales_summary, rep_details, reps_summary, sku_not_ordered,
                          third_party_sales_summary, top_customers)

from side_func import identify_file, get_file_name, get_csv_columns

load_dotenv()

fastapi_url = os.getenv('FASTAPI_URL')

file_type = identify_file()
st.set_page_config( page_icon='icon.ico', page_title=file_type)
css='''
<style>
    section.main > div {max-width:75rem}
    section.main > div {min-width:75rem}
</style>
'''
st.markdown(css, unsafe_allow_html=True)


UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)



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
            
        pre_prompt = f'''Please do not include any tables, graphs, or code imports in your response, just answer to the query and make it attractive: {prompt} ?'''

        result = chat_with_agent(pre_prompt, file_path)
        
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
        #api_key = os.getenv('Chat_Api') ,openai_api_key=api_key
        agent = create_csv_agent(
            ChatOpenAI(temperature=0, model="gpt-4o"),
            file_path,
            verbose=True,
            agent_type=AgentType.OPENAI_FUNCTIONS
        )
        result = agent.invoke(input_string)
        return result['output']
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

def cache_df(last_uploaded_file_path):
    if 'df' not in st.session_state:
            st.session_state["df"] = pd.read_csv(last_uploaded_file_path)
    try:
        df = st.session_state["df"]
    except Exception as e:
        st.warning("There is some error with data, try to update the session")
    return df

def id_str(Id):
    id_str = str(Id)
    if not str(id_str).startswith('$'):
        return f"{float(id_str):.0f}"
    else:
        return id_str

def format_phone_number(phone_number):
    phone_str = str(phone_number)
    if len(phone_str) == 11 and phone_str.startswith("1"):
        return f"+{phone_str[0]} ({phone_str[1:4]}) {phone_str[4:7]}-{phone_str[7:]}"
    elif len(phone_str) == 10:
        return f"({phone_str[:3]}) {phone_str[3:6]}-{phone_str[6:]}"
    elif not str(phone_str).startswith('$'):
        temp = f"{float(phone_str):.0f}" #TODO maybe try str format and first element show only
        temp1 = str(temp)
        if len(temp1) == 11 and temp1.startswith("1"):
            return f"+{temp1[0]} ({temp1[1:4]}) {temp1[4:7]}-{temp1[7:]}"
        elif len(temp1) == 10:
            return f"({temp1[:3]}) {temp1[3:6]}-{temp1[6:]}"
    else:
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
    #st.write(st.session_state)
    df = cache_df(last_uploaded_file_path)
    df.index = range(1, len(df) + 1)
    file_type = identify_file()

    #session block
    if 'AI_appear' not in st.session_state:
        st.session_state.AI_appear = False
    if 'input_text' not in st.session_state:
        st.session_state.input_text = ''
    if 'my_input' not in st.session_state:
        st.session_state.input_text = ''
    if 'chat_clicked' not in st.session_state:
        st.session_state.chat_clicked = False
    if 'continue_clicked' not in st.session_state:
        st.session_state.continue_clicked = False
    #keyy = os.getenv('OPENAI_API_KEY')
    #st.write(keyy)
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
                st.success(f"This is  {st.session_state.report_name} type. File is available for visualization.")

                if file_type == "Representative Details report":
                    df_show = df.copy()
                    df_show['Id'] = df_show['Id'].apply(id_str)
                    df_show['Phone number'] = df_show['Phone number'].apply(format_phone_number)
                    st.dataframe(df_show,width=2500, use_container_width=False)
                
                elif file_type == "Customer Details report":
                    df_show = df.copy()
                    #df_show['Phone number'] = df_show['Phone number'].apply(format_phone_number)  #error with this report
                    st.dataframe(df_show,width=2500, use_container_width=False)
                    
                elif file_type == "Top Customers report":
                    df_show = df.copy()
                    #df_show['Phone number'] = df_show['Phone number'].apply(format_phone_number)  #error with this report
                    #df_show['Contact phone'] = df_show['Contact phone'].apply(format_phone_number)  #TODO error with this report
                    df_show['Total sales'] = df_show['Total sales'].apply(add_dollar_sign)
                    st.dataframe(df_show,width=2500, use_container_width=False)
                
                elif file_type == "Order Sales Summary report":
                    df_show = df.copy()
                    df_show['Id'] = df_show['Id'].apply(id_str)
                    df_show['Id'] = df_show['Id'].apply(id_str)
                    df_show['Grand total'] = df_show['Grand total'].apply(add_dollar_sign)
                    df_show['Item specific discount'] = df_show['Item specific discount'].apply(add_dollar_sign)
                    df_show['Manufacturer specific discount'] = df_show['Manufacturer specific discount'].apply(add_dollar_sign)
                    df_show['Total invoice discount'] = df_show['Total invoice discount'].apply(add_dollar_sign)
                    df_show['Customer discount'] = df_show['Customer discount'].apply(add_dollar_sign)
                    df_show['Balance'] = df_show['Balance'].apply(add_dollar_sign)
                    st.dataframe(df_show,width=2500, use_container_width=False)
                
                elif file_type == "SKU's Not Ordered report":
                    df_show = df.copy()
                    df_show['Wholesale price'] = df_show['Wholesale price'].apply(add_dollar_sign)
                    df_show['Retail price'] = df_show['Retail price'].apply(add_dollar_sign)
                    df_show['Total revenue'] = df_show['Total revenue'].apply(add_dollar_sign)
                    st.dataframe(df_show,width=2500, use_container_width=False)
                
                elif file_type == "Reps Summary report":
                    df_show = df.copy()
                    df_show['Id'] = df_show['Id'].apply(id_str)
                    df_show['Total revenue'] = df_show['Total revenue'].apply(add_dollar_sign)
                    st.dataframe(df_show,width=2500, use_container_width=False)
                
                elif file_type == "Low Stock Inventory report":
                    df_show = df.copy()
                    df_show['Wholesale price'] = df_show['Wholesale price'].apply(add_dollar_sign)
                    df_show['Retail price'] = df_show['Retail price'].apply(add_dollar_sign)
                    st.dataframe(df_show,width=2500, use_container_width=False)

                elif file_type =="Best Sellers report":
                    df_show = df.copy()
                    df_show['Wholesale price'] = df_show['Wholesale price'].apply(add_dollar_sign)
                    df_show['Retail price'] = df_show['Retail price'].apply(add_dollar_sign)
                    df_show['Total revenue'] = df_show['Total revenue'].apply(add_dollar_sign)
                    st.dataframe(df_show,width=2500, use_container_width=False)

                elif file_type == "3rd Party Sales Summary report":
                    df_show = df.copy()
                    df_show['Id'] = df_show['Id'].apply(id_str)
                    df_show['Grand total'] = df_show['Grand total'].apply(add_dollar_sign)
                    df_show['Item specific discount'] = df_show['Item specific discount'].apply(add_dollar_sign)
                    df_show['Manufacturer specific discount'] = df_show['Manufacturer specific discount'].apply(add_dollar_sign)
                    df_show['Total invoice discount'] = df_show['Total invoice discount'].apply(add_dollar_sign)
                    df_show['Customer discount'] = df_show['Customer discount'].apply(add_dollar_sign)
                    st.dataframe(df_show,width=2500, use_container_width=False)

                elif file_type == "Current Inventory report":
                    df_show = df.copy()
                    df_show['Wholesale price'] = df_show['Wholesale price'].apply(add_dollar_sign)
                    df_show['Retail price'] = df_show['Retail price'].apply(add_dollar_sign)
                    st.dataframe(df_show,width=2500, use_container_width=False)
                else:
                    st.dataframe(df,width=2500, use_container_width=False)
    except:
        st.warning("Data display error, try reloading the report")

    with stylable_container(
        key="chat-ai",
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
                width: 110px;
                height: 55px;
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
        
        def click_AI_Appear():
            st.session_state.AI_appear = True
        button_AI_appear = st.button('Use AI technology', on_click=click_AI_Appear, key=888)
        if st.session_state.AI_appear:
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
                            border-radius: 13%;
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
                    tab1, tab2 = st.tabs(["Chat","Build a chart"])
                    #with col1:
                    @st.dialog("Analyze Selected Data")
                    def AI_info():
                        def click_cont_button():
                            st.session_state.continue_clicked = True

                        st.markdown("""
                            <div class="custom-container">
                                <p>By clicking 'Continue', you will be connected to ChatGPT service. All information will be provided directly to the OpenAI server. For more information, read their privacy documents.</p>
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
                            key="custom-button",
                            css_styles=["""
                                button {
                                    background-color: #409A65;
                                    border: 2px solid #47A06D;
                                    color: #ffffff;
                                    padding: 0px;
                                    text-align: center;
                                    text-decoration: none;
                                    border-radius: 3%;
                                    font-size: 17px;
                                    margin: 4px 2px;
                                    border-style: solid;
                                    width: 450px;
                                    height: 50px;
                                    line-height: 30px;
                                    position: relative;
                                }
                                """,
                                """
                                button:hover {
                                    background-color: #47A06D;
                                    box-shadow: 0 12px 16px 0 rgba(0,0,0,0.24), 0 17px 50px 0 rgba(0,0,0,0.19);
                                    color: #ffffff;
                                }"""],
                        ):
                            button1_clicked = st.button('Continue', on_click=click_cont_button, key="custom-button")
                        with stylable_container(
                            "red",
                            css_styles="""
                button {
                    background-color: #ffffff;
                    border: 2px solid #FF0000;
                    color: ##FF0000;
                    padding: 0px;
                    text-align: center;
                    text-decoration: none;
                    border-radius: 3%;
                    font-size: 17px;
                    margin: 4px 2px;
                    border-style: solid;
                    width: 450px;
                    height: 50px;
                    line-height: 30px;
                    position: relative;
                }
                """,
                        ):
                            button2_clicked = st.button('Decline', key=31)

                        if button1_clicked:
                            st.rerun() #close window

                        if button2_clicked:
                            st.rerun() #close window

                    with tab1:
                        st.info("Chat with GPT")

                        option = st.selectbox(
                            "Choose a query to analyze your CSV data:",  #label is not visible
                            ("Provide a brief summary of key insights for a business owner",
                             "Identify the top 3 critical dependencies in the data",
                             "Summarize the most important performance metrics from this CSV",
                             "Highlight any significant trends or patterns in the data",
                             "Generate a concise report of data anomalies or outliers"),
                            index=None,
                            placeholder="Select one of the frequently asked questions?",
                            label_visibility="collapsed")

                        def update_text():
                            st.session_state['input_text'] = st.session_state['my_input']

                        if option is None:
                            st.session_state['input_text'] = st.text_area(label='Enter your query:', key='my_input' , placeholder="Enter your request to start a chat", label_visibility="collapsed", on_change=update_text)
                            #st.write(f"Current text in func: {st.session_state['input_text']}")
                            input_text = st.session_state['input_text']
                        else:
                            st.session_state['input_text'] = st.text_area(value=option, label='Enter your query:', placeholder="Type your question or message and press ‘Submit’", label_visibility="collapsed", on_change=update_text)
                            option = None
                            input_text = st.session_state['input_text']
                   
                        if input_text is not None:
                            #\\
                            def click_button():
                                st.session_state.chat_clicked = True


                            with stylable_container(
                                key="custom-Submit1_button",
                                css_styles=["""
                                    button {
                                        background-color: #409A65;
                                        border: 2px solid #47A06D;
                                        color: #ffffff;
                                        padding: 0px;
                                        text-align: center;
                                        text-decoration: none;
                                        border-radius: 13%;
                                        font-size: 17px;
                                        margin: 4px 2px;
                                        border-style: solid;
                                        width: 100px;
                                        height: 45px;
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
                                button_Submit1 = st.button('Submit', on_click=click_button, key=1)

                            if st.session_state.chat_clicked == True:
                                if st.session_state.continue_clicked == False:
                                    AI_info() 
                                else:

                                    if st.session_state.chat_clicked:
                                        if 'input_text' in st.session_state:
                                            #st.write(f"Current text: {st.session_state['input_text']}")
                                            user_prompt = st.session_state['input_text']
                                        
                                        st.session_state.chat_clicked = False #TODO real needed?
                                        try:
                                            if "chat_result" not in st.session_state:
                                                #with st.spinner(text="In progress..."):
                                                    #st.write(user_prompt)
                                                    st.session_state["chat_result"] = chat_with_file(user_prompt, last_uploaded_file_path)
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
                                                    chat_result = chat_with_file(user_prompt, last_uploaded_file_path)
                                                    st.session_state["chat_result"] = chat_result
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
                            if 'continue_clicked' not in st.session_state:
                                st.session_state.continue_clicked = False

                            def click_button():
                                st.session_state.plot_clicked = True


                            with stylable_container(
                                key="custom-Submit2_button",
                                css_styles=["""
                                    button {
                                        background-color: #409A65;
                                        border: 2px solid #47A06D;
                                        color: #ffffff;
                                        padding: 0px;
                                        text-align: center;
                                        text-decoration: none;
                                        border-radius: 13%;
                                        font-size: 17px;
                                        margin: 4px 2px;
                                        border-style: solid;
                                        width: 100px;
                                        height: 45px;
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
                                if st.session_state.continue_clicked == False:
                                    AI_info()
                                else:
                                    #\\\
                                    if st.session_state.plot_clicked:
                                        #st.session_state.click = True
                                        st.info("Plotting your Query: " + input_text2)
                                        #result = build_some_chart(df, input_text2)
                                        try:
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
                                                plot_result = test_plot_maker(df, input_text2)
                                                st.plotly_chart(plot_result)
                                            #st.success(result)
                                        #except Exception as e:
                                        #    raise ValueError(f"An error occurred: {str(e)}")
                                        except Exception as e:
                                            st.warning("There is some error with data visualization, try to make query more details")


    #css for inform button
    with stylable_container(
            key="custom-inform-button",
            css_styles=["""
                button {
                    background-color: #ffffff;
                    border: 2px solid #47A06D;
                    color: #47A06D;
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
            'Customer Details report': customer_details.report_func
        }
        if file_type in report_function_map:
            report_function_map[file_type](df)
        else:
            if df.empty:
                st.warning("### This data report is empty - try downloading another one to get better visualizations")
            else:
                st.warning("###Unrecognized error")






def main_viz():
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
    clean_csv_files(UPLOAD_DIR)
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
    main_viz()