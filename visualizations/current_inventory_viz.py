import plotly.express as px
import pandas as pd
import streamlit as st
import numpy as np
from plotly.colors import sequential
from plotly.colors import qualitative
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
        # Use .isna() instead of np.isnan() because it's safer for different data types
        if data[col].isna().any():
            # ASSIGN the result back to data[col] instead of using inplace=True
            data[col] = data[col].fillna(0)
            print(f"Warning: Column '{col}' contains missing values (NaN). Filled with 0.")

    # Remove currency symbols and thousands separators
    data[numeric_cols] = data[numeric_cols].replace('[$,]', '', regex=True).astype(float)

    return data
#Analyzes and visualizes the total inventory value by category
def df_analyze_inventory_value_by_category(df):
    if df['Wholesale Price'].dtype == 'object':
        df['Wholesale Price'] = pd.to_numeric(df['Wholesale Price'].str.replace(',', '').str.replace('$ ', ''))

    # Calculate 'Inventory Value'
    df["Inventory Value"] = df["Available Cases (QTY)"] * df["Wholesale Price"]
    category_value = df.groupby("Category Name")["Inventory Value"].sum().reset_index()

    # Create the bar chart using plotly.graph_objects
    fig = go.Figure()

    for _, row in category_value.iterrows():
        fig.add_trace(go.Bar(
            x=[row['Category Name']],
            y=[row['Inventory Value']],
            name=row['Category Name'],
            hovertemplate='<b>%{x}</b><br>Inventory Value: $%{y:,.2f}<extra></extra>'
        ))

    # Update the layout for better visualization
    fig.update_layout(
        xaxis_title="Category",
        yaxis_title="Inventory Value",
        showlegend=True,
        legend_title_text='Category',
        legend=dict(
            x=1.05,
            y=1,
            bgcolor='rgba(255, 255, 255, 0)',
            bordercolor='rgba(255, 255, 255, 0)',
            title_font=dict(size=12),
            font=dict(size=10),
            orientation='v'  # Change to 'h' if you want the legend below the plot
        ),
        margin=dict(r=150)  # Adjust the right margin to make space for the legend
    )

    # Display the plot in Streamlit
    st.plotly_chart(fig, use_container_width=True)

    

def df_analyze_quantity_vs_retail_price(df):
    for col in ["Retail Price", "Wholesale Price"]:
        if df[col].dtype == 'object':
            df[col] = pd.to_numeric(df[col].str.replace(',', '').str.replace('$ ', ''))

    df['Wholesale Price'] = df['Wholesale Price'].fillna(0)

    categories = df["Category Name"].unique()
    colors = px.colors.qualitative.Plotly[:len(categories)]
    color_map = dict(zip(categories, colors))

    fig = go.Figure()

    for category in categories:
        df_cat = df[df["Category Name"] == category]
        fig.add_trace(go.Scatter(
            x=df_cat["Available Cases (QTY)"],
            y=df_cat["Retail Price"],
            mode='markers',
            marker=dict(
                size=df_cat["Wholesale Price"],
                sizemode='area',
                sizeref=2.*max(df["Wholesale Price"])/(40.**2),
                color=color_map[category]
            ),
            name=category,
            hovertemplate='<b>%{text}</b><br>Available Cases: %{x}<br>Retail Price: $%{y:.2f}<br>Wholesale Price: $%{marker.size:.2f}<extra></extra>',
            text=df_cat["Category Name"]
        ))

    fig.update_layout(
        xaxis_title="Available Cases",
        yaxis_title="Retail Price",
        template="plotly_white",
        showlegend=True,
        legend_title_text='Category'
    )

    st.plotly_chart(fig, use_container_width=True)

    

#Analyzing Inventory Value Distribution Across Manufacturers
def df_analyze_inventory_value_by_manufacturer(df):
    # Ensure 'Wholesale price' is numeric
    if df['Wholesale Price'].dtype == 'object':
        df['Wholesale Price'] = pd.to_numeric(df['Wholesale Price'].str.replace(',', '').str.replace('$ ', ''))

    # Calculate 'Inventory Value'
    df["Inventory Value"] = df["Available Cases (QTY)"] * df["Wholesale Price"]
    manufacturer_value = df.groupby("Manufacturer Name")["Inventory Value"].sum().reset_index()

    # Create the bar chart using plotly.graph_objects
    fig = go.Figure()

    for _, row in manufacturer_value.iterrows():
        fig.add_trace(go.Bar(
            x=[row['Manufacturer Name']],
            y=[row['Inventory Value']],
            name=row['Manufacturer Name'],
            hovertemplate='<b>%{x}</b><br>Inventory Value: $%{y:,.2f}<extra></extra>'
        ))

    # Update the layout for better visualization
    fig.update_layout(
        xaxis_title="Manufacturer",
        yaxis_title="Inventory Value",
        showlegend=True,
        legend_title_text='Manufacturer',
        legend=dict(
            x=1.05,
            y=1,
            bgcolor='rgba(255, 255, 255, 0)',
            bordercolor='rgba(255, 255, 255, 0)',
            title_font=dict(size=12),
            font=dict(size=10),
            orientation='v'  # Change to 'h' if you want the legend below the plot
        ),
        margin=dict(r=150)  # Adjust the right margin to make space for the legend
    )

    # Display the plot in Streamlit
    st.plotly_chart(fig, use_container_width=True)

    

#Analyzes and visualizes the average inventory value per unit for each product
def df_analyze_inventory_value_per_unit(df):
    # Ensure 'Wholesale price' is numeric
    if df['Wholesale Price'].dtype == 'object':
        df['Wholesale Price'] = pd.to_numeric(df['Wholesale Price'].str.replace(',', '').str.replace('$ ', ''))
    
    # Calculate 'Inventory Value per Unit'
    df["Inventory Value per Unit"] = pd.to_numeric(df["Wholesale Price"], errors='coerce')
    df = df.dropna(subset=["Inventory Value per Unit"])
    
    # Calculate total value per product
    df['Total Value'] = df["Inventory Value per Unit"] * df['Available Cases (QTY)']
    
    # Group by 'Product name' and sum the 'Total Value'
    product_value = df.groupby("Product Name")["Total Value"].sum().reset_index()

    fig = go.Figure()
    product_value['Product Name'] = product_value['Product Name'].apply(lambda x: x[:35] + '...' if len(x) > 35 else x)
    for _, row in product_value.iterrows():
        fig.add_trace(go.Bar(
            x=[row['Product Name']],
            y=[row['Total Value']],
            name=row['Product Name'],
            hovertemplate=
            '<b>%{x}</b><br>' +
            'Total Value: $%{y:,.2f}<extra></extra>',
        ))
    
    # Update the layout for better visualization
    fig.update_layout(
        xaxis_title="Product",
        yaxis_title="Total Value",
        showlegend=True,
        legend=dict(
            x=1.05,
            y=1,
            bgcolor='rgba(255, 255, 255, 0)',
            bordercolor='rgba(255, 255, 255, 0)',
            title_font=dict(size=12),
            font=dict(size=10),
            orientation='v'  # Change to 'h' if you want the legend below the plot
        ),
        margin=dict(r=150)  # Adjust the right margin to make space for the legend
    )

    # Display the plot in Streamlit
    st.plotly_chart(fig, use_container_width=True)

    

# Comparing Average Retail Prices Across Categories
def df_compare_average_retail_prices(df, threshold=0.01):
    # Convert 'Retail price' to numeric if necessary
    if df['Retail Price'].dtype == 'object':
        df['Retail Price'] = pd.to_numeric(df['Retail Price'].str.replace(',', '').str.replace('$ ', ''), errors='coerce')

    average_prices = df.groupby("Category Name")["Retail Price"].mean()
    
    total_sum = average_prices.sum()
    average_prices_percentage = average_prices / total_sum
    
    # Group smaller categories into 'Other'
    main_data = average_prices[average_prices_percentage >= threshold]
    other_data = average_prices[average_prices_percentage < threshold]
    
    if not other_data.empty:
        other_sum = other_data.sum()
        main_data['Other'] = other_sum
    
    # Create the pie chart
    fig = go.Figure(data=[go.Pie(
        values=main_data.values,
        labels=main_data.index,
        hole=0.3,  # Create a donut chart
        marker=dict(colors=px.colors.qualitative.Vivid),
        textinfo='percent+label',
        hovertemplate=
        '<b>%{label}</b><br>' +
        'Average Retail Price: $%{value:,.2f}<extra></extra>'
    )])

    fig.update_layout(
        showlegend=True,
        margin=dict(t=0, b=0, l=0, r=0)
    )

    st.plotly_chart(fig, use_container_width=True)

    
