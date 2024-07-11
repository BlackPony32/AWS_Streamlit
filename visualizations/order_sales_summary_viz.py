import streamlit as st
import pandas as pd
import plotly.express as px
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

#_________________Sales Trends Function  (with Plotly)_______________________________
def visualize_sales_trends1(data, customer_col='Customer', product_col='Product name', 
                           grand_total_col='Grand total', qty_col='QTY'):
    
        st.subheader("Total Sales by Customer (Top 10)")
        top_customers = data.groupby(customer_col)[grand_total_col].sum().nlargest(10)
        # Create the plot
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=top_customers.index,
            y=top_customers.values,
            marker=dict(
                color=top_customers.values,
                colorscale='Bluyl'
            ),
            hovertemplate='<b>Customer:</b> %{x}<br><b>Sales Amount:</b> $%{y:.2f}<extra></extra>'
        ))
        
        # Update the layout
        fig.update_layout(
            title="Top 10 Customers by Sales Amount",
            xaxis_tickangle=45,
            yaxis_title="Sales Amount",
            xaxis_title="Customer",
            coloraxis_colorbar=dict(title="Sales Amount")
        )
        
        # Display the chart in Streamlit
        st.plotly_chart(fig, use_container_width=True)

def visualize_sales_trends2(data, customer_col='Customer', product_col='Product name', 
                           grand_total_col='Grand total', qty_col='QTY'):
    
        data['Created at'] = pd.to_datetime(data['Created at'])

        # Specify the column name for grand total
        grand_total_col = 'Grand total'

        # Calculate monthly sales
        monthly_sales = data.groupby(pd.Grouper(key='Created at', freq='M'))[grand_total_col].sum()

        # Create the plot
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=monthly_sales.index,
            y=monthly_sales.values,
            mode='lines+markers',
            name='Sales Amount',
            hovertemplate='<b>Month:</b> %{x}<br><b>Sales Amount:</b> $%{y:.2f}<extra></extra>'
        ))
        
        # Update the layout
        fig.update_layout(
            title="Monthly Sales Trend",
            xaxis_title="Month",
            yaxis_title="Sales Amount",
            hovermode='x unified'
        )

        # Update the layout
        #fig.update_layout(xaxis_title="Month", yaxis_title="Sales Amount")
        st.plotly_chart(fig, use_container_width=True)

#_________________Product Analysis Function (with Plotly)___________________________
def visualize_product_analysis1(data, product_col='Product name', grand_total_col='Grand total'):
    product_data = data.groupby(product_col)[grand_total_col].agg(['sum', 'count']).sort_values(by='sum', ascending=False)

   
    fig = go.Figure(data=[go.Pie(
        labels=product_data.index, 
        values=product_data['sum'],
        hovertemplate='<b>%{label}</b><br>Sales: $%{value:.2f}<br>Percentage: %{percent}<extra></extra>',
        textinfo='percent+label'
    )])
    fig.update_layout(
        title="Total Sales by Product",
        colorway=px.colors.qualitative.Vivid,
        title_x=0.5
    )
    st.plotly_chart(fig)


def visualize_product_analysis2(data, product_col='Product name', grand_total_col='Grand total'):
    product_data = data.groupby(product_col)[grand_total_col].agg(['sum', 'count']).sort_values(by='sum', ascending=False)

    fig = go.Figure(data=[go.Bar(
        x=product_data.index, 
        y=product_data['count'],
        hovertemplate='<b>%{x}</b><br>Orders: %{y}<extra></extra>',
        marker_color=product_data['count'],
        marker_colorscale='Cividis'
    )])
    fig.update_layout(
        title="Distribution of Orders by Product",
        xaxis_title="Product",
        yaxis_title="Number of Orders",
        xaxis_tickangle=45,
        title_x=0.5
    )
    st.plotly_chart(fig, use_container_width=True)

#_________________Discount Analysis Function (with Plotly)__________________________
def visualize_discount_analysis1(data, discount_type_col='Discount type', total_discount_col='Total invoice discount'):
    """Visualizes discount analysis by type and top customers."""

    st.subheader("Discount Amount by Customer (Top 10)")
    
    # Group by customer and sum the total discounts, then get the top 10 customers
    top_customers_discount = data.groupby('Customer')[total_discount_col].sum().nlargest(10)
    
    # Create a bar chart for top customers by discount amount
    fig = go.Figure(data=[go.Bar(
        x=top_customers_discount.index, 
        y=top_customers_discount.values,
        hovertemplate='<b>%{x}</b><br>Discount Amount: $%{y:,.2f}<extra></extra>',
        marker=dict(color=top_customers_discount.values, colorscale='Pinkyl')
    )])
    fig.update_layout(
        title="Discount Amount by Customer (Top 10)", 
        xaxis_tickangle=45, 
        yaxis_title="Discount Amount", 
        xaxis_title="Customer",
        title_x=0.5,
        coloraxis_showscale=False  # Hide the color scale
    )
    
    # Display the bar chart in Streamlit
    st.plotly_chart(fig, use_container_width=True)


def visualize_discount_analysis2(data, discount_type_col='Discount type', total_discount_col='Total invoice discount'):
    """Visualizes discount analysis by type and top customers."""
    
    # Group by discount type and sum the total discounts
    discount_amounts = data.groupby(discount_type_col)[total_discount_col].sum().sort_values(ascending=False)
    
    # Create a pie chart for discount distribution by type
    fig = go.Figure(data=[go.Pie(
        labels=discount_amounts.index, 
        values=discount_amounts.values,
        hovertemplate='<b>%{label}</b><br>Discount Amount: $%{value:,.2f}<br>Percentage: %{percent}<extra></extra>',
        textinfo='percent+label'
    )])
    fig.update_layout(
        title="Distribution of Discount Amount by Type",
        colorway=px.colors.qualitative.Set3,
        title_x=0.5
    )
    
    # Display the pie chart in Streamlit
    st.plotly_chart(fig, use_container_width=True)


# _________________Delivery Analysis Function (with Plotly)___________________________
def visualize_delivery_analysis1(data, delivery_status_col='Delivery status', 
                                delivery_method_col='Delivery methods'):
    
    
    
        st.subheader("Number of Orders by Delivery Status")
        delivery_status_counts = data[delivery_status_col].value_counts()
        
        # Create a pie chart for delivery status distribution
        fig = go.Figure(data=[go.Pie(
            labels=delivery_status_counts.index, 
            values=delivery_status_counts.values,
            hovertemplate='<b>%{label}</b><br>Orders: %{value}<br>Percentage: %{percent}<extra></extra>',
            textinfo='percent+label'
        )])
        fig.update_layout(
            title="Distribution of Orders by Delivery Status",
            colorway=px.colors.qualitative.Light24,
            title_x=0.5
        )
        
        # Display the pie chart in Streamlit
        st.plotly_chart(fig, use_container_width=True)


def visualize_delivery_analysis2(data, delivery_status_col='Delivery status', 
                                delivery_method_col='Delivery methods'):
    
        st.subheader("Number of Orders by Delivery Method")
        delivery_method_counts = data[delivery_method_col].value_counts()
        
        # Create a pie chart for delivery method distribution
        fig = go.Figure(data=[go.Pie(
            labels=delivery_method_counts.index, 
            values=delivery_method_counts.values,
            hovertemplate='<b>%{label}</b><br>Orders: %{value}<br>Percentage: %{percent}<extra></extra>',
            textinfo='percent+label'
        )])
        fig.update_layout(
            title="Distribution of Orders by Delivery Method",
            colorway=px.colors.qualitative.Bold,
            title_x=0.5
        )
        st.plotly_chart(fig, use_container_width=True)

# _________________Payment Analysis Function (with Plotly)___________________________
def visualize_payment_analysis(data, payment_status_col='Payment status'):
    payment_status_counts = data[payment_status_col].value_counts()

    # Create a pie chart for payment status distribution
    fig = go.Figure(data=[go.Pie(
        labels=payment_status_counts.index, 
        values=payment_status_counts.values,
        hovertemplate='<b>%{label}</b><br>Orders: %{value}<br>Percentage: %{percent}<extra></extra>',
        textinfo='percent+label'
    )])
    fig.update_layout(
        colorway=px.colors.qualitative.Pastel,
        title_x=0.5
    )

    # Display the pie chart in Streamlit
    st.plotly_chart(fig, use_container_width=True)

    

# _________________Combined Analysis Function (with Plotly)___________________________
def visualize_combined_analysis1(data, product_col='Product name', 
                               grand_total_col='Grand total', qty_col='QTY', 
                               delivery_status_col='Delivery status'):

        st.subheader("Relationship between Quantity and Amount (by Product)")
        scatter_data = [
            go.Scatter(
                x=data[data[product_col] == product][qty_col], 
                y=data[data[product_col] == product][grand_total_col],
                mode='markers',
                name=product,
                text=data[data[product_col] == product][product_col],
                hovertemplate='Quantity: %{x}<br>Sales Amount: %{y}<br>Product: %{text}<extra></extra>'
            ) for product in data[product_col].unique()
        ]
        fig = go.Figure(data=scatter_data)
        fig.update_layout(
            title="Relationship between Quantity and Amount (by Product)",
            xaxis_title="Quantity",
            yaxis_title="Sales Amount",
            xaxis_tickangle=45,
            template="plotly_white"
        )
        st.plotly_chart(fig, use_container_width=True)



def visualize_combined_analysis2(data, product_col='Product name', 
                               grand_total_col='Grand total', qty_col='QTY', 
                               delivery_status_col='Delivery status'):

        st.subheader("Number of Orders by Product and Delivery Status")
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
            title="Number of Orders by Product and Delivery Status",
            xaxis_title="Product",
            yaxis_title="Number of Orders",
            barmode='group',
            xaxis_tickangle=45,
            template="plotly_white"
        )
        st.plotly_chart(fig, use_container_width=True)
