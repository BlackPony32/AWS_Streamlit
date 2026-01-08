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
        # Use .isna() instead of np.isnan() because it's safer for different data types
        if data[col].isna().any():
            # ASSIGN the result back to data[col] instead of using inplace=True
            data[col] = data[col].fillna(0)
            print(f"Warning: Column '{col}' contains missing values (NaN). Filled with 0.")

    # Remove currency symbols and thousands separators
    data[numeric_cols] = data[numeric_cols].replace('[$,]', '', regex=True).astype(float)

    return data


def Quantity_Delivered_Returned_Per_Rep_Visualization(df):
    """
    Creates a grouped bar chart of total quantity delivered and returned per sales representative.
    
    Parameters:
    - df (pd.DataFrame): DataFrame containing the sales data.
    """
    # Define required columns
    required_columns = ["Fulfilled By", "Type", "Delivery Status", "QTY"]
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        st.error(f"Missing columns: {', '.join(missing_columns)}")
        return

    # Filter for fulfilled status
    df_fulfilled = df[df["Delivery Status"] == "FULFILLED"]

    # Split into delivery and return DataFrames
    df_delivery = df_fulfilled[df_fulfilled["Type"] == "Delivery"]
    df_return = df_fulfilled[df_fulfilled["Type"] == "Return"]

    # Aggregate quantities by sales representative
    delivery_agg = df_delivery.groupby("Fulfilled By")["QTY"].sum().reset_index()
    return_agg = df_return.groupby("Fulfilled By")["QTY"].sum().reset_index()

    # Merge the aggregates, filling missing values with 0
    merged = pd.merge(delivery_agg, return_agg, on="Fulfilled By", how="outer", 
                      suffixes=("_delivered", "_returned")).fillna(0)

    # Create Plotly figure
    fig = go.Figure()

    # Add bar for delivered quantities
    fig.add_trace(go.Bar(
        x=merged["Fulfilled By"],
        y=merged["QTY_delivered"],
        name="Delivered",
        marker_color="rgb(55, 83, 109)",
        text=merged["QTY_delivered"],
        textposition="auto",
        hovertemplate="<b>%{x}</b><br>Delivered: %{y:.2f}<extra></extra>"
    ))

    # Add bar for returned quantities
    fig.add_trace(go.Bar(
        x=merged["Fulfilled By"],
        y=merged["QTY_returned"],
        name="Returned",
        marker_color="rgb(255, 127, 80)",
        text=merged["QTY_returned"],
        textposition="auto",
        hovertemplate="<b>%{x}</b><br>Returned: %{y:.2f}<extra></extra>"
    ))

    # Update layout for grouped bars
    fig.update_layout(
        xaxis_title="Sales Representative",
        yaxis_title="Total Quantity",
        barmode="group",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        template="plotly",
        xaxis_tickangle=-45
    )

    # Format text on bars
    fig.update_traces(texttemplate="%{text:.2f}")

    # Display the chart in Streamlit
    st.plotly_chart(fig, use_container_width=True)

def Quantity_Sold_Over_Time_Visualization(df):
    """
    Creates a line chart of total quantity sold over time, aggregated by month.
    
    Parameters:
    - df (pd.DataFrame): DataFrame containing the sales data.
    """
    # Define required columns
    required_columns = ["Fulfill Date", "Type", "Delivery Status", "QTY"]
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        st.error(f"Missing columns: {', '.join(missing_columns)}")
        return

    # Filter for delivered and fulfilled items
    df_filtered = df[(df["Type"] == "Delivery") & (df["Delivery Status"] == "FULFILLED")].copy()

    # Convert Fulfill date to datetime (assuming MM/DD/YYYY format)
    df_filtered["Fulfill Date"] = pd.to_datetime(df_filtered["Fulfill Date"], format='mixed', errors='coerce')

    # Extract month period for grouping
    df_filtered["Month"] = df_filtered["Fulfill Date"].dt.to_period("M")

    # Aggregate quantities by month
    monthly_sales = df_filtered.groupby("Month")["QTY"].sum().reset_index()

    # Convert Month to string for plotting
    monthly_sales["Month"] = monthly_sales["Month"].astype(str)

    # Sort by month to ensure chronological order
    monthly_sales = monthly_sales.sort_values("Month")

    # Create Plotly figure
    fig = go.Figure()

    # Add line trace with markers
    fig.add_trace(go.Scatter(
        x=monthly_sales["Month"],
        y=monthly_sales["QTY"],
        mode="lines+markers",
        name="Quantity Sold",
        line=dict(color="rgb(55, 83, 109)"),
        marker=dict(size=8),
        text=monthly_sales["QTY"],
        hovertemplate="<b>Month: %{x}</b><br>Quantity Sold: %{y:.2f}<extra></extra>"
    ))

    # Update layout
    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Total Quantity Sold",
        template="plotly",
        xaxis_tickangle=-45
    )

    # Display the chart in Streamlit
    st.plotly_chart(fig, use_container_width=True)
