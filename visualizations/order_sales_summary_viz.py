import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import plotly.graph_objects as go
import textwrap

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

#_________________Sales Trends Function  (with Plotly)_______________________________
def visualize_sales_trends1(data, customer_col='Customer', product_col='Product name', 
                            grand_total_col='Grand total', qty_col='QTY', 
                            order_id_col='Order Id'):  # Add order_id_col parameter
    
    # Convert Grand Total to numeric
    data[grand_total_col] = pd.to_numeric(data[grand_total_col], errors='coerce')
    data = data.dropna(subset=[grand_total_col])
    
    # Step 1: Remove duplicate orders (keep first occurrence per Order ID)
    unique_orders = data.drop_duplicates(subset=[order_id_col])
    
    # Step 2: Calculate total sales per customer using de-duplicated data
    customer_sales = unique_orders.groupby(customer_col)[grand_total_col].sum()
    top_customers = customer_sales.nlargest(10)

    # Create plot
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=top_customers.index,
        y=top_customers.values,
        marker=dict(color=top_customers.values, colorscale='Bluyl'),
        hovertemplate='<b>Customer:</b> %{x}<br><b>Sales Amount:</b> $%{y:.2f}<extra></extra>'
    ))
    
    fig.update_layout(
        title="Top 10 Customers by Sales Amount",
        xaxis_tickangle=45,
        yaxis_title="Sales Amount",
        xaxis_title="Customer"
    )
    st.plotly_chart(fig, use_container_width=True)


def visualize_sales_trends2(data, customer_col='Customer', product_col='Product name', 
                           grand_total_col='Grand total', qty_col='QTY',
                           order_id_col='Order Id'):  # Add order_id_col parameter
    
    # Convert date and Grand Total
    data['Created at'] = pd.to_datetime(data['Created at'])
    data[grand_total_col] = pd.to_numeric(data[grand_total_col], errors='coerce')
    data = data.dropna(subset=[grand_total_col])
    
    # Step 1: Remove duplicate orders
    unique_orders = data.drop_duplicates(subset=[order_id_col])
    
    # Step 2: Group de-duplicated data by month
    monthly_sales = unique_orders.groupby(pd.Grouper(key='Created at', freq='M'))[grand_total_col].sum()

    # Create plot
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=monthly_sales.index,
        y=monthly_sales.values,
        mode='lines+markers',
        name='Sales Amount',
        hovertemplate='<b>Month:</b> %{x|%b %Y}<br><b>Sales Amount:</b> $%{y:.2f}<extra></extra>'
    ))
    
    fig.update_layout(
        title="Monthly Sales Trend",
        xaxis_title="Month",
        yaxis_title="Sales Amount",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

#_________________Product Analysis Function (with Plotly)___________________________
def visualize_product_analysis1(data, product_col='Product name', 
                                product_total_col='Product Total',  # Use item-level total
                                threshold=0.03):
    """Visualize total sales by product with a pie chart, grouping smaller products into 'Other'."""
    
    # Convert to numeric and handle NaNs
    data[product_total_col] = pd.to_numeric(data[product_total_col], errors='coerce')
    data = data.dropna(subset=[product_total_col])
    
    # Group by product using PRODUCT-level total (not order total)
    product_data = data.groupby(product_col)[product_total_col].agg(['sum', 'count']).sort_values(by='sum', ascending=False)

    # Calculate percentages
    total_sales_sum = product_data['sum'].sum()
    product_data['percentage'] = product_data['sum'] / total_sales_sum

    # Group smaller products into 'Other'
    main_data = product_data[product_data['percentage'] >= threshold]
    other_data = product_data[product_data['percentage'] < threshold]

    if not other_data.empty:
        other_sales_sum = other_data['sum'].sum()
        other_row = pd.DataFrame({
            'sum': [other_sales_sum],
            'count': [other_data['count'].sum()],
            'percentage': [other_sales_sum / total_sales_sum]
        }, index=['Other'])
        main_data = pd.concat([main_data, other_row])

    # Create pie chart
    fig = go.Figure(data=[go.Pie(
        labels=main_data.index, 
        values=main_data['sum'],
        hovertemplate='<b>%{label}</b><br>Sales: $%{value:.2f}<br>Percentage: %{percent}<extra></extra>',
        textinfo='percent+label'
    )])
    
    fig.update_layout(
        title="Total Sales by Product",
        colorway=px.colors.qualitative.Vivid,
        title_x=0.5,
        height=550
    )
    st.plotly_chart(fig, use_container_width=True)


def visualize_product_analysis2(data, product_col='Product name'):
    """Distribution of orders by product (uses count of occurrences, not Grand total)"""
    
    # Simply count product occurrences (no need for totals)
    product_counts = data.groupby(product_col).size().sort_values(ascending=False)
    
    # Wrap long labels
    wrapped_labels = [textwrap.fill(text, width=15) for text in product_counts.index]

    fig = go.Figure(data=[go.Bar(
        x=wrapped_labels, 
        y=product_counts.values,
        hovertemplate='<b>%{x}</b><br>Orders: %{y}<extra></extra>',
        marker=dict(
            color=product_counts.values, 
            colorscale='Cividis',
            showscale=False
        )
    )])
    
    fig.update_layout(
        title="Distribution of Orders by Product",
        xaxis_title="Product",
        yaxis_title="Number of Orders",
        xaxis_tickangle=-45,
        title_x=0.5,
        height=600
    )
    st.plotly_chart(fig, use_container_width=True)

#_________________Discount Analysis Function (with Plotly)__________________________
def visualize_discount_analysis1(data, discount_type_col='Discount type', total_discount_col='Total invoice discount'):
    """Visualizes discount analysis by type and top customers, with error handling."""
    
    st.subheader("Discount Amount by Customer (Top 10)")

    # Check if DataFrame is empty
    if data.empty:
        st.warning("The dataset is empty.")
        return

    # Check if required columns are present
    if not set([discount_type_col, total_discount_col, 'Customer']).issubset(data.columns):
        st.warning(f"Required columns are missing: {', '.join([discount_type_col, total_discount_col, 'Customer'])}")
        return

    # Ensure the total discount column is numeric
    data[total_discount_col] = pd.to_numeric(data[total_discount_col], errors='coerce')

    # Handle potential NaN values after conversion
    data = data.dropna(subset=[total_discount_col])

    # Group by customer and sum the total discounts, then get the top 10 customers
    top_customers_discount = data.groupby('Customer')[total_discount_col].sum().nlargest(10)

    # Check if there are no non-zero discounts
    if top_customers_discount.sum() == 0:
        st.warning("Visualization is not available when all discounts are zero")
        return

    # Create a bar chart for top customers by discount amount
    fig = go.Figure(data=[go.Bar(
        x=top_customers_discount.index, 
        y=top_customers_discount.values,
        hovertemplate='<b>%{x}</b><br>Discount Amount: $%{y:,.2f}<extra></extra>',
        marker=dict(
            color=top_customers_discount.values, 
            colorscale='Viridis',  
            showscale=False  
        )
    )])

    # Update the layout
    fig.update_layout(
        xaxis_tickangle=-45, 
        yaxis_title="Discount Amount ($)", 
        xaxis_title="Customer",
        height=500,  
        template="plotly_white"  
    )

    # Display the bar chart in Streamlit
    st.plotly_chart(fig, use_container_width=True)

def visualize_discount_analysis2(data, discount_type_col='Discount type', total_discount_col='Total invoice discount'):
    """Visualizes discount analysis by type and top customers, with error handling."""
    
    # Check if DataFrame is empty
    if data.empty:
        st.warning("The dataset is empty.")
        return

    # Check if required columns are present
    if not set([discount_type_col, total_discount_col]).issubset(data.columns):
        st.warning(f"Required columns are missing: {', '.join([discount_type_col, total_discount_col])}")
        return

    # Group by discount type and sum the total discounts
    discount_amounts = data.groupby(discount_type_col)[total_discount_col].sum().sort_values(ascending=False)

    # Check if there are no non-zero discounts
    if discount_amounts.sum() == 0:
        st.warning("Visualization is not available when all discounts are zero")
        return
    
    # Create a pie chart for discount distribution by type
    fig = go.Figure(data=[go.Pie(
        labels=discount_amounts.index, 
        values=discount_amounts.values,
        hovertemplate='<b>%{label}</b><br>Discount Amount: $%{value:,.2f}<br>Percentage: %{percent}<extra></extra>',
        textinfo='percent+label',
        marker=dict(colors=px.colors.qualitative.Set3)  
    )])

    # Update the layout
    fig.update_layout(
        colorway=px.colors.qualitative.Set3,
        height=500  
    )
    
    # Display the pie chart in Streamlit
    st.plotly_chart(fig, use_container_width=True)


# _________________Delivery Analysis Function (with Plotly)___________________________
def visualize_delivery_analysis1(data, delivery_status_col='Delivery status'):
    """Visualizes the distribution of orders by delivery status."""
    
    # Calculate the counts for each delivery status
    delivery_status_counts = data[delivery_status_col].value_counts()
    
    # Create a pie chart for delivery status distribution
    fig = go.Figure(data=[go.Pie(
        labels=delivery_status_counts.index, 
        values=delivery_status_counts.values,
        hovertemplate='<b>%{label}</b><br>Orders: %{value}<br>Percentage: %{percent}<extra></extra>',
        textinfo='percent+label',
        marker=dict(colors=px.colors.qualitative.Light24)  # Use a distinct color palette
    )])
    
    fig.update_layout(
        title="Distribution of Orders by Delivery Status",
        title_x=0.5,
        height=500  # Adjust height for better display
    )
    
    # Display the pie chart in Streamlit
    st.plotly_chart(fig, use_container_width=True)

def visualize_delivery_analysis2(data, delivery_method_col='Delivery methods'):
    """Visualizes the distribution of orders by delivery method."""
    
    # Calculate the counts for each delivery method
    delivery_method_counts = data[delivery_method_col].value_counts()
    
    # Create a pie chart for delivery method distribution
    fig = go.Figure(data=[go.Pie(
        labels=delivery_method_counts.index, 
        values=delivery_method_counts.values,
        hovertemplate='<b>%{label}</b><br>Orders: %{value}<br>Percentage: %{percent}<extra></extra>',
        textinfo='percent+label',
        marker=dict(colors=px.colors.qualitative.Bold)  # Use a distinct color palette
    )])
    
    fig.update_layout(
        title="Distribution of Orders by Delivery Method",
        title_x=0.5,
        height=500  # Adjust height for better display
    )
    
    # Display the pie chart in Streamlit
    st.plotly_chart(fig, use_container_width=True)

def visualize_payment_analysis(data, payment_status_col='Payment status'):
    """Visualizes the distribution of orders by payment status."""
    
    # Calculate the counts for each payment status
    payment_status_counts = data[payment_status_col].value_counts()

    # Create a pie chart for payment status distribution
    fig = go.Figure(data=[go.Pie(
        labels=payment_status_counts.index, 
        values=payment_status_counts.values,
        hovertemplate='<b>%{label}</b><br>Orders: %{value}<br>Percentage: %{percent}<extra></extra>',
        textinfo='percent+label',
        marker=dict(colors=px.colors.qualitative.Pastel)  # Use a distinct color palette
    )])
    
    fig.update_layout(
        title="Distribution of Orders by Payment Status",
        title_x=0.5,
        height=500  # Adjust height for better display
    )
    
    # Display the pie chart in Streamlit
    st.plotly_chart(fig, use_container_width=True)


# _________________Combined Analysis Function (with Plotly)___________________________
def visualize_combined_analysis1(data, product_col='Product name', 
                                 product_total_col='Product Total',  # Use item-level total
                                 qty_col='QTY',
                                 delivery_status_col='Delivery status'):
    
    # Convert to numeric
    data[product_total_col] = pd.to_numeric(data[product_total_col], errors='coerce')
    data[qty_col] = pd.to_numeric(data[qty_col], errors='coerce')
    data = data.dropna(subset=[product_total_col, qty_col])
    
    max_legend_length = 30
    top_products = data[product_col].value_counts().nlargest(20).index  # Limit to top 20

    scatter_data = [
        go.Scatter(
            x=data[data[product_col] == product][qty_col], 
            y=data[data[product_col] == product][product_total_col],  # Use PRODUCT total
            mode='markers',
            name=(product[:max_legend_length] + '...' if len(product) > max_legend_length else product),
            text=data[data[product_col] == product][product_col],
            hovertemplate='<b>%{text}</b><br>Quantity: %{x}<br>Sales: $%{y:.2f}<extra></extra>'
        ) for product in top_products  # Only plot top products
    ]
    
    fig = go.Figure(data=scatter_data)
    fig.update_layout(
        xaxis_title="Quantity",
        yaxis_title="Sales Amount",
        xaxis_tickangle=45,
        template="plotly_white",
        legend=dict(title="Products", font=dict(size=9))
    )
    st.plotly_chart(fig, use_container_width=True)


def visualize_combined_analysis2(data, product_col='Product name', 
                               grand_total_col='Grand total', qty_col='QTY', 
                               delivery_status_col='Delivery status'):

        histogram_data = [
            go.Histogram(
                x=data[data[delivery_status_col] == status][product_col],
                name=status,
                marker=dict(line=dict(width=0.5)),
                hovertemplate='Product: %{x}<br>Number of Orders: %{y}<br>Delivery Status: %{text}<extra></extra>',
                text=data[data[delivery_status_col] == status][delivery_status_col]
            ) for status in data[delivery_status_col].unique()
        ]
        fig = go.Figure(data=histogram_data)
        fig.update_layout(
            xaxis_title="Product",
            yaxis_title="Number of Orders",
            barmode='group',
            xaxis_tickangle=45,
            template="plotly_white"
        )
        st.plotly_chart(fig, use_container_width=True)
