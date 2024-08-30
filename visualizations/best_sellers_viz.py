import plotly.express as px
import pandas as pd
import streamlit as st
import numpy as np
from plotly.colors import sequential
import plotly.graph_objects as go
import plotly.colors as colors
from plotly.subplots import make_subplots

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


def create_available_cases_plot(df):
    df['Available cases (QTY)'] = df['Available cases (QTY)'].astype(int)
    df['Color'] = df['Available cases (QTY)'].apply(lambda x: 'Out of Stock' if x < 0 else 'In Stock')

    fig = px.scatter(
        df, 
        y='Product name', 
        x='Available cases (QTY)', 
        title='Available Cases (QTY)', 
        text='Available cases (QTY)',
        color='Color',  
        color_discrete_map={'Out of Stock': 'red', 'In Stock': 'green'}
    )

    fig.update_traces(
        textposition="top center",
        hovertemplate="<b>Product:</b> %{y}<br><b>Available Cases (QTY):</b> %{x}<br><b>Inventory status</b> <extra></extra>"
    )

    fig.update_layout(
        xaxis_tickangle=45, 
        plot_bgcolor='white', 
        xaxis={'categoryorder':'total descending'},
        legend_title_text='Inventory Status'
    )

    st.plotly_chart(fig, use_container_width=True)


def product_analysis_app1(df):
    st.title("Product Sales Analysis")
    product_data = df.groupby('Product name')[['Total revenue', 'Cases sold']].sum()

    
    fig1 = px.pie(
        product_data, 
        values='Total revenue', 
        names=product_data.index,
        hole=0.3, 
        color_discrete_sequence=px.colors.qualitative.Light24
    )
    fig1.update_traces(
        textposition='inside', 
        textinfo='percent+label',
        hovertemplate="<b>Product:</b> %{label}<br><b>Total Revenue:</b> %{value} $<br><b>Percentage:</b> %{percent}<extra></extra>"
    )
    st.plotly_chart(fig1, use_container_width=True)
        
def product_analysis_app2(df):
    st.title("Product Sales Analysis")
    product_data = df.groupby('Product name')[['Total revenue', 'Cases sold']].sum()

    fig2 = px.funnel(
            product_data, 
            x='Cases sold', 
            y=product_data.index,
            title="Total Cases Sold by Product",
            color=product_data.index,
            color_discrete_sequence=px.colors.qualitative.Bold
        )

    fig2.update_traces(
        hovertemplate="<b>Product:</b> %{y}<br><b>Cases Sold:</b> %{x}<extra></extra>"
    )
    st.plotly_chart(fig2, use_container_width=True)
        


def create_cases_revenue_relationship_plot(df):
    fig = px.scatter(
        df, 
        x='Cases sold', 
        y='Total revenue', 
        color='Total revenue',
        color_continuous_scale='Greens',
        size='Total revenue',  
        hover_data={'Product name': True, 'Cases sold': True, 'Total revenue': True}
    )

    fig.update_traces(
        textposition='top center',
        hovertemplate="<b>Product:</b> %{customdata[0]}<br><b>Cases Sold:</b> %{x}<br><b>Total Revenue:</b> %{y} $<extra></extra>"
    )

    fig.update_layout(
        xaxis_title="Cases Sold", 
        yaxis_title="Total Revenue", 
        plot_bgcolor='white'
    )

    st.plotly_chart(fig, use_container_width=True)


def price_comparison_app1(df):
    average_prices = df.groupby('Category name')[['Wholesale price', 'Retail price']].mean()

    
    fig1 = go.Figure(go.Bar(
        x=average_prices.index,
        y=average_prices['Wholesale price'],
        marker_color=colors.qualitative.Pastel,
        hovertemplate="<b>Category:</b> %{x}<br><b>Wholesale Price:</b> $%{y:.2f}<extra></extra>"
    ))
    fig1.update_layout(
        title="Average Wholesale Price by Category",
        xaxis_title="Category",
        yaxis_title="Wholesale Price",
        xaxis_tickangle=45,
        hovermode="closest"
    )
    st.plotly_chart(fig1, use_container_width=True)


def price_comparison_app2(df):
    average_prices = df.groupby('Category name')[['Wholesale price', 'Retail price']].mean()

    fig2 = go.Figure(go.Bar(
        x=average_prices.index,
        y=average_prices['Retail price'],
        marker_color=colors.qualitative.Pastel,
        hovertemplate="<b>Category:</b> %{x}<br><b>Retail Price:</b> $%{y:.2f}<extra></extra>"
    ))
    fig2.update_layout(
        title="Average Retail Price by Category",
        xaxis_title="Category",
        yaxis_title="Retail Price",
        xaxis_tickangle=45,
        hovermode="closest"
    )
    st.plotly_chart(fig2, use_container_width=True)

def create_revenue_vs_profit_plot1(df):
    # Calculate Profit
    df['Profit'] = (df['Retail price'] - df['Wholesale price']) * df['Cases sold']
    
    # Calculate Revenue by Category (if needed)
    category_revenue = df.groupby('Category name')['Total revenue'].sum()

    # Assign colors to products
    product_colors = colors.qualitative.Plotly
    product_color_map = {product: color for product, color in zip(df['Product name'].unique(), product_colors)}
    
    # Create the plot
    fig1 = go.Figure()
    
    for product in df['Product name'].unique():
        product_data = df[df['Product name'] == product]
        
        # Use .get() to avoid KeyError
        color = product_color_map.get(product, 'green')  # Default to 'green' if product not found in product_color_map
        
        fig1.add_trace(go.Scatter(
            x=product_data['Total revenue'],
            y=product_data['Profit'],
            mode='markers',
            marker=dict(
                color=color,
                size=10
            ),
            name=product,
            text=product_data['Product name'],
            hovertemplate="<b>Product:</b> %{text}<br><b>Revenue:</b> $%{x:.2f}<br><b>Profit:</b> $%{y:.2f}<extra></extra>"
        ))
    
    fig1.update_layout(
        title="Total Revenue vs. Profit per Product",
        xaxis_title="Total Revenue",
        yaxis_title="Profit",
        hovermode="closest",
        legend=dict(title="Products")
    )
    
    # Display the plot in Streamlit
    st.plotly_chart(fig1, use_container_width=True)

    
            
def create_revenue_vs_profit_plot2(df):
    df['Profit'] = (df['Retail price'] - df['Wholesale price']) * df['Cases sold']
    category_revenue = df.groupby('Category name')['Total revenue'].sum()
    
    fig2 = go.Figure(go.Pie(
        values=category_revenue.values,
        labels=category_revenue.index,
        hole=0.3,
        marker=dict(colors=colors.qualitative.Vivid),
        textposition='inside',
        textinfo='percent+label',
        hovertemplate="<b>Category:</b> %{label}<br><b>Revenue:</b> $%{value:.2f}<br><b>Percentage:</b> %{percent}<extra></extra>"
    ))
    fig2.update_layout(
        title="Revenue Breakdown by Category",
        hovermode="closest"
    )
    st.plotly_chart(fig2, use_container_width=True)
        