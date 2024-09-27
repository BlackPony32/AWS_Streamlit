import plotly.express as px
import pandas as pd
import streamlit as st
import numpy as np
import plotly.graph_objects as go

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

def low_stock_analysis_app1(df, threshold=0.01):
    category_counts = df.groupby("Category name")["Product name"].count().reset_index()
    total_sum = category_counts["Product name"].sum()
    
    # Calculate percentages
    category_counts['percentage'] = category_counts["Product name"] / total_sum
    
    # Group smaller categories into 'Other'
    main_data = category_counts[category_counts['percentage'] >= threshold]
    other_data = category_counts[category_counts['percentage'] < threshold]
    
    if not other_data.empty:
        other_sum = other_data["Product name"].sum()
        other_row = pd.DataFrame({'Category name': ['Other'], 'Product name': [other_sum], 'percentage': [other_sum / total_sum]})
        main_data = pd.concat([main_data, other_row], ignore_index=True)
    
    fig1 = go.Figure(go.Pie(
        labels=main_data["Category name"],
        values=main_data["Product name"],
        hole=0.3,
        textinfo='percent+label',
        marker=dict(colors=px.colors.qualitative.Pastel),
        hovertemplate="<b>Category:</b> %{label}<br><b>Count:</b> %{value}<br><b>Percentage:</b> %{percent}<extra></extra>"
    ))
    fig1.update_layout(
        legend=dict(title="Category", orientation="h", y=1.1, x=0.5, xanchor='center'),
        margin=dict(t=0, b=0, l=0, r=0)
    )
    st.plotly_chart(fig1, use_container_width=True)


def low_stock_analysis_app2(df):
    # Filter data for non-null wholesale prices (allowing negative and zero quantities)
    df_valid_prices = df[df['Wholesale price'].notna()]

    # Check if the DataFrame is empty after filtering
    if df_valid_prices.empty:
        st.write("No data available for plotting. Please check your dataset.")
        return

    fig2 = go.Figure(data=go.Scatter(
        x=df_valid_prices["Wholesale price"],
        y=df_valid_prices["Available cases (QTY)"],
        mode='markers',
        marker=dict(
            size=10,  # Increased marker size for better visibility
            color=df_valid_prices["Wholesale price"],
            colorscale='Viridis',  # Choose a colorscale for better visualization
            showscale=True
        ),
        text=df_valid_prices['Product name'],
        hovertemplate="<b>%{text}</b><br>Wholesale Price: %{x}<br>Available Cases (QTY): %{y}<extra></extra>"
    ))

    fig2.update_layout(
        xaxis=dict(
            title="Wholesale Price",
            range=[df_valid_prices["Wholesale price"].min() - 1, df_valid_prices["Wholesale price"].max() + 1]
        ),
        yaxis=dict(
            title="Available Cases (QTY)",
            range=[df_valid_prices["Available cases (QTY)"].min() - 1, df_valid_prices["Available cases (QTY)"].max() + 1]
        ),
        template="plotly_white",
        margin=dict(t=0, b=0, l=0, r=0)
    )

    st.plotly_chart(fig2, use_container_width=True)


    

def create_profit_margin_analysis_plot(df):
    # Calculate Profit Margin
    df["Profit Margin"] = df["Retail price"] - df["Wholesale price"]
    df_sorted = df.sort_values(by="Profit Margin", ascending=False)

    # Create the bar chart with a green color scale
    fig = go.Figure(go.Bar(
        x=df_sorted['Product name'],
        y=df_sorted['Profit Margin'],
        marker=dict(color=df_sorted['Profit Margin'], colorscale='greens'),  # Green color scale
        text=df_sorted['Profit Margin'].apply(lambda x: f'${x:,.2f}'),
        hovertemplate="<b>%{x}</b><br>Profit Margin: %{y:.2f}<extra></extra>"
    ))

    # Update layout with more style and clarity
    fig.update_layout(
        xaxis_title="Product Name",
        yaxis_title="Profit Margin (in $)",
        xaxis_tickangle=45,
        xaxis={'categoryorder': 'total descending'},
        template="plotly_white",
        plot_bgcolor="rgba(0,0,0,0)",  # Transparent background
        yaxis=dict(
            gridcolor='lightgray', 
            title_font=dict(size=14, color='darkgreen'),
            tickfont=dict(size=15)  # Make y-axis labels bigger
        ),
        font=dict(family="Arial, sans-serif", size=12),
        xaxis_title_font=dict(size=14, color='darkgreen'),
        hoverlabel=dict(bgcolor="lightgreen", font_size=12),
        legend=dict(title="Profit Margin", orientation="h", y=1.1, x=0.5, xanchor='center')
    )

    # Display the chart in Streamlit
    st.plotly_chart(fig, use_container_width=True)



def create_low_stock_by_manufacturer_bar_plot(df):
    low_stock_counts = df.groupby("Manufacturer name")["Product name"].count().reset_index()

    fig = go.Figure(go.Bar(
        x=low_stock_counts['Manufacturer name'],
        y=low_stock_counts['Product name'],
        marker=dict(color=low_stock_counts['Product name']),
                    #colorscale='Pastel'),
        text=low_stock_counts['Product name'],
        hovertemplate="<b>%{x}</b><br>Number of Low Stock Items: %{y}<extra></extra>"
    ))
    
    fig.update_layout(
        xaxis_title="Manufacturer",
        yaxis_title="Number of Low Stock Items",
        xaxis_tickangle=45,
        xaxis={'categoryorder': 'total descending'},
        template="plotly_white",
        legend=dict(title="Manufacturer", orientation="h", y=1.1, x=0.5, xanchor='center')
    ) 
    
    st.plotly_chart(fig, use_container_width=True)



#Analyzing the correlation Between Price and Available Quantity
def create_interactive_price_vs_quantity_plot(df):
    df['Wholesale price'] = pd.to_numeric(df['Wholesale price'], errors='coerce')

    fig = px.scatter(
        df, 
        x="Wholesale price", 
        y="Available cases (QTY)", 
        trendline="ols",
        template="plotly_white",
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    
    fig.update_traces(
        hovertemplate="<b>Product:</b> %{text}<br><b>Wholesale Price:</b> %{x}<br><b>Available Cases (QTY):</b> %{y}<extra></extra>",
        text=df['Product name']
    )
    
    fig.update_layout(
        xaxis_title="Wholesale Price", 
        yaxis_title="Available Cases (QTY)",
        legend=dict(title="Category", orientation="h", y=1.1, x=0.5, xanchor='center')
    )
    
    st.plotly_chart(fig, use_container_width=True)


def create_quantity_price_ratio_plot(df):
    df['Retail price'] = pd.to_numeric(df['Retail price'], errors='coerce')
    df["QTY/Price Ratio"] = df["Available cases (QTY)"] / df["Retail price"]
    df_sorted = df.sort_values(by="QTY/Price Ratio")

    fig = px.bar(
        df_sorted, 
        y='Product name', 
        x='QTY/Price Ratio', 
        color='QTY/Price Ratio', 
        orientation='h',
        color_continuous_scale='purples', 
        text='QTY/Price Ratio',
        template="plotly_white"
    )
    
    fig.update_traces(
        texttemplate='%{text:.2f}', 
        textposition='outside',
        hovertemplate="<b>Product:</b> %{y}<br><b>QTY/Price Ratio:</b> %{x:.2f}<extra></extra>"
    )
    
    fig.update_layout(
        xaxis_title="QTY/Price Ratio", 
        yaxis_title="Product Name",
        legend=dict(title="Category", orientation="h", y=1.1, x=0.5, xanchor='center')
    )
    
    st.plotly_chart(fig, use_container_width=True)
