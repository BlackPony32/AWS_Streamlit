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


def Business_Payment_Insights(df):
    # 1. Data Cleaning: Group and sum the financial metrics
    # We take the top 15 businesses by total volume to keep the chart clean
    agg_df = df.groupby("Business Name").agg({
        "Payment Amount": "sum",
        "Order Balance": "sum"
    }).reset_index()
    
    agg_df['Total_Volume'] = agg_df['Payment Amount'] + agg_df['Order Balance']
    agg_df = agg_df.sort_values(by='Total_Volume', ascending=False).head(15)
    
    # Shorten Business Names for the X-axis
    agg_df['Display Name'] = agg_df['Business Name'].apply(lambda x: x[:25] + '...' if len(x) > 25 else x)

    # 2. Create Plotly Figure
    fig = go.Figure()

    # Trace for Payments (Success/Green)
    fig.add_trace(go.Bar(
        x=agg_df['Display Name'],
        y=agg_df['Payment Amount'],
        name='Total Paid ($)',
        marker_color='rgb(34, 139, 34)', 
        text=agg_df['Payment Amount'],
        textposition='auto',
        hovertemplate="<b>%{x}</b><br>Paid: $%{y:,.2f}<extra></extra>"
    ))

    # Trace for Balance (Debt/Red)
    fig.add_trace(go.Bar(
        x=agg_df['Display Name'],
        y=agg_df['Order Balance'],
        name='Outstanding Balance ($)',
        marker_color='rgb(220, 20, 60)', 
        text=agg_df['Order Balance'],
        textposition='auto',
        hovertemplate="<b>%{x}</b><br>Balance: $%{y:,.2f}<extra></extra>"
    ))

    # 3. Layout updates
    fig.update_layout(
        xaxis_title="Business Name",
        yaxis_title="Amount ($)",
        barmode="group",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(t=50, b=50, l=10, r=10),
        template="plotly_white",
        xaxis_tickangle=-45
    )

    fig.update_traces(texttemplate='$%{text:,.0f}')

    # Plot in Streamlit
    st.plotly_chart(fig, use_container_width=True)


def Payment_Distribution_Treemap(df):
    # 1. Clean Data
    df_clean = df.copy()
    df_clean['Payment Amount'] = pd.to_numeric(df_clean['Payment Amount'], errors='coerce').fillna(0)
    
    # 2. Group minor Payment Methods into "Other" to improve readability
    # (Keep only methods that appear more than 5 times)
    method_counts = df_clean['Payment Method'].value_counts()
    top_methods = method_counts[method_counts > 5].index.tolist()
    df_clean['Payment Method Grouped'] = df_clean['Payment Method'].apply(
        lambda x: x if x in top_methods else 'Other Methods'
    )
    
    # 3. Aggregate for Hierarchy
    # Level 1: Status
    status_agg = df_clean.groupby('Payment Status')['Payment Amount'].sum().reset_index()
    # Level 2: Status + Method
    method_agg = df_clean.groupby(['Payment Status', 'Payment Method Grouped'])['Payment Amount'].sum().reset_index()
    
    # 4. Prepare Treemap Arrays
    ids, labels, parents, values = [], [], [], []
    
    # Add Status Rectangles
    for _, row in status_agg.iterrows():
        ids.append(row['Payment Status'])
        labels.append(f"<b>{row['Payment Status']}</b>")
        parents.append("")
        values.append(row['Payment Amount'])
        
    # Add Method Rectangles
    for _, row in method_agg.iterrows():
        ids.append(f"{row['Payment Status']}-{row['Payment Method Grouped']}")
        labels.append(row['Payment Method Grouped'])
        parents.append(row['Payment Status'])
        values.append(row['Payment Amount'])

    # 5. Create Figure
    fig = go.Figure(go.Treemap(
        ids=ids,
        labels=labels,
        parents=parents,
        values=values,
        textinfo="label+value+percent parent",
        branchvalues="total",
        marker=dict(colorscale='Blues'), # Professional color palette
        hovertemplate='<b>%{label}</b><br>Total: $%{value:,.2f}<br>% of Status: %{percentParent:.1%}<extra></extra>'
    ))

    fig.update_layout(
        margin=dict(t=10, l=10, r=10, b=10),
        height=500,
        template="plotly_white"
    )

    st.plotly_chart(fig, use_container_width=True)