import plotly.express as px
import pandas as pd
import streamlit as st
import numpy as np
from plotly.colors import sequential
from plotly.colors import qualitative
import plotly.graph_objects as go
import plotly.colors as colors

def preprocess_data(data):
    """
    Data preprocessing: data type conversion and cleaning.

    Args:
        data: A Pandas DataFrame with the source data.

    Returns:
        Pandas DataFrame with the processed data.
    """

    # Identify numeric columns automatically
    numeric_cols = data.select_dtypes(include=np.number).columns

    # Process numeric columns
    for col in numeric_cols:
        # Check for missing values (NaN)
        if np.isnan(data[col]).any():
            # Fill missing values with 0 (you can choose another strategy)
            data[col].fillna(0, inplace=True)
            print(f"Warning: Column '{col}' contains missing values (NaN). Filled with 0.")

    # Remove currency symbols and thousands separators
    data[numeric_cols] = data[numeric_cols].replace('[$,]', '', regex=True).astype(float)

    return data



def Sales_Performance_Visualization(df):
    # Ensure required columns exist
    required_columns = [
        "Business Name",
        "Cases sold (Direct)",
        "Cases sold (3rd party)"
    ]
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        st.error(f"The following required columns are missing from the dataset: {', '.join(missing_columns)}")
        return
    
    # Aggregate data (if needed)
    aggregated_data = df.groupby("Business Name").agg(
        direct_sales=("Cases sold (Direct)", "sum"),
        third_party_sales=("Cases sold (3rd party)", "sum")
    ).reset_index()
    
    # Create the figure
    fig = go.Figure()
    
    # Add bars for direct sales
    fig.add_trace(go.Bar(
        x=aggregated_data['Business Name'],
        y=aggregated_data['direct_sales'],
        name='Direct Sales',
        marker_color='rgb(55, 83, 109)',
        text=aggregated_data['direct_sales'],
        textposition='auto',
        hovertemplate="<b>Business Name: %{x}</b><br>Sales Representative: Direct Sales" "<br>Cases Sold: %{y:.0f}<extra></extra>"
        
    ))
    
    # Add bars for 3rd party sales
    fig.add_trace(go.Bar(
        x=aggregated_data['Business Name'],
        y=aggregated_data['third_party_sales'],
        name='3rd Party Sales',
        marker_color='rgb(255, 127, 80)',
        text=aggregated_data['third_party_sales'],
        textposition='auto',
        hovertemplate="<b>Business Name: %{x}</b><br>Sales Representative: 3rd Party Sales" "<br>Cases Sold: %{y:.0f}<extra></extra>"
        
    ))
    
    # Update layout
    fig.update_layout(
        xaxis_title="Business Name",
        yaxis_title="Cases Sold",
        barmode="group",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        template="plotly",
        xaxis_tickangle=-45  # Rotate x-axis labels for better readability
        
        
    )
    
    # Update traces to format text
    fig.update_traces(texttemplate='%{text:.0f}')
    
    # Plotting the figure using Streamlit
    st.plotly_chart(fig, use_container_width=True)

def Sales_Trend_Visualization(df):
    # Ensure required columns exist
    required_columns = ["Name", "Date", "Cases sold total"]
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        st.error(f"The following required columns are missing from the dataset: {', '.join(missing_columns)}")
        return
    
    # Ensure 'Date' is a datetime object
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    
    # Filter rows with valid dates
    filtered_data = df.dropna(subset=['Date'])
    
    # Aggregate data by Name and Date
    aggregated_data = filtered_data.groupby(["Name", "Date"]).agg(
        total_cases_sold=("Cases sold total", "sum")
    ).reset_index()
    
    # Create the figure
    fig = go.Figure()
    
    # Add traces for each Name
    for name in aggregated_data['Name'].unique():
        sales_data = aggregated_data[aggregated_data['Name'] == name]
        fig.add_trace(go.Scatter(
            x=sales_data['Date'],
            y=sales_data['total_cases_sold'],
            mode='lines+markers',
            name=name,
            marker=dict(size=8),
            line=dict(width=2),
            text=sales_data['total_cases_sold'],
            textposition='top center',
            hovertemplate="<b>Date: %{x}</b><br>Sales Representative: " + name + "<br>Total cases sold: %{y:.0f}<extra></extra>"
        
        ))
    
    # Update layout
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Total Cases Sold",
        legend_title="Sales Representative",
        template="plotly",
    )
    
    # Plotting the figure using Streamlit
    st.plotly_chart(fig, use_container_width=True)
