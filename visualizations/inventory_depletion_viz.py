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
    """
    Visualizes inventory depletion for the top products based on quantity.
    
    Args:
        df (pd.DataFrame): Input DataFrame containing 'Business name' and product quantity data.
    """
    # Copy the DataFrame to avoid modifying the original
    data = df.copy()
    columns_to_remove = ['Billing Zip', 'Billing zip', 'Shipping zip', 'Shipping Zip']

    # Drop columns if they exist
    data = data.drop(columns=[col for col in columns_to_remove if col in df.columns])
    # Validate presence of 'Business name' column
    if 'Business name' not in data.columns:
        st.error("The column 'Business name' is missing in the dataset.")
        return

    # Select numeric columns dynamically
    numeric_columns = data.select_dtypes(include="number").columns
    if numeric_columns.empty:
        st.error("No numeric columns found in the dataset.")
        return

    # Identify the top 12 products by total quantity
    top_products = (
        data[numeric_columns]
        .sum()
        .nlargest(12)  # Top 12 by total quantity
        .index
    )

    # Filter data for 'Business name' and top products
    filtered_data = data[['Business name'] + list(top_products)]

    # Create a Plotly figure
    fig = go.Figure()

    # Add bar traces for each top product
    for product in top_products:
        fig.add_trace(
        go.Bar(
            x=filtered_data['Business name'],  # X-axis data
            y=filtered_data[product],         # Y-axis data (quantities for the product)
            name=product,                     # Product name
            text=filtered_data[product],      # Add text to display on bars
            textposition="auto",              # Position text automatically
            hovertemplate="<b>Business: %{x}</b><br>Product: " + product + "<br>Quantity: %{y:.0f}<extra></extra>"
        )
    )

    # Update figure layout
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
        xaxis_tickangle=-45
    )

    # Update trace text format
    fig.update_traces(texttemplate="%{text:.0f}")

    # Display the chart in Streamlit
    st.plotly_chart(fig, use_container_width=True)
