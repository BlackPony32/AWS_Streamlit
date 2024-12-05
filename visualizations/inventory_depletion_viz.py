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

def Inventory_Depletion_Visualization(df):
    # Copying the data to avoid modifying the original dataframe
    data = df.copy()
    
    # Ensure 'Business name' column exists in the data
    if 'Business name' not in data.columns:
        st.error("The column 'Business name' is missing in the dataset.")
        return
    
    # Selecting numeric columns dynamically
    product_columns = data.select_dtypes(include="number").columns
    
    if product_columns.empty:
        st.error("No numeric columns found in the dataset.")
        return
    
    # Calculate total quantities for each product and filter top 10
    top_products = (
        data[product_columns]
        .sum()
        .nlargest(12)  # Get the top 10 products by total quantity
        .index
    )
    
    # Filter data for only the top 10 products
    filtered_data = data[['Business name'] + list(top_products)]
    
    # Create the figure
    fig = go.Figure()
    
    # Bar chart for each product in the top 10
    for product in top_products:
        fig.add_trace(go.Bar(
            x=filtered_data['Business name'],
            y=filtered_data[product],
            name=product,
            text=filtered_data[product],
            textposition='auto'
        ))
    
    # Update layout
    fig.update_layout(
        xaxis_title="Business Name",
        yaxis_title="Quantity",
        barmode="stack",
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
