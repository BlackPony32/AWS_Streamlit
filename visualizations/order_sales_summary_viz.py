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
        # Use .isna() instead of np.isnan() because it's safer for different data types
        if data[col].isna().any():
            # ASSIGN the result back to data[col] instead of using inplace=True
            data[col] = data[col].fillna(0)
            print(f"Warning: Column '{col}' contains missing values (NaN). Filled with 0.")

    # Remove currency symbols and thousands separators
    data[numeric_cols] = data[numeric_cols].replace('[$,]', '', regex=True).astype(float)

    return data

#_________________Sales Trends Function  (with Plotly)_______________________________
def visualize_sales_trends1(data, customer_col='Customer', product_col='Product Name', 
                            grand_total_col='Grand Total', qty_col='QTY', 
                            order_id_col='Order ID'):  # Add order_id_col parameter
    
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

def visualize_sales_trends2(data, customer_col='Customer', product_col='Product Name', 
                           grand_total_col='Grand Total', qty_col='QTY',
                           order_id_col='Order ID'):  # Add order_id_col parameter
    
    # Convert date and Grand Total
    data['Date Created'] = pd.to_datetime(data['Date Created'])
    data[grand_total_col] = pd.to_numeric(data[grand_total_col], errors='coerce')
    data = data.dropna(subset=[grand_total_col])
    
    # Step 1: Remove duplicate orders
    unique_orders = data.drop_duplicates(subset=[order_id_col])
    
    # Step 2: Group de-duplicated data by month
    monthly_sales = unique_orders.groupby(pd.Grouper(key='Date Created', freq='ME'))[grand_total_col].sum()

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
def visualize_product_analysis1(data, product_col='Product Name', 
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


def visualize_product_analysis2(data, product_col='Product Name'):
    """Distribution of orders by product (uses count of occurrences, not Grand total)"""
    

    product_counts = data.groupby(product_col).size().sort_values(ascending=False)
    
    # 1. Get the full labels as strings
    full_labels = product_counts.index.astype(str).tolist()
    # 2. Create truncated labels (max 15 chars + '...') for the X-axis
    truncated_labels = [text[:15] + '...' if len(text) > 15 else text for text in full_labels]

    fig = go.Figure(data=[go.Bar(
        x=truncated_labels,            # X-axis gets the short names
        y=product_counts.values,
        customdata=full_labels,        # We pass the full names in behind the scenes
        
        # 3. Tell the hovertemplate to look at %{customdata} instead of %{x}
        hovertemplate='<b>%{customdata}</b><br>Orders: %{y}<extra></extra>',
        
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
def visualize_discount_analysis1(data, discount_type_col='Discount Type', total_discount_col='Total Invoice Discount'):
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

def visualize_discount_analysis2(data, discount_type_col='Discount Type', total_discount_col='Total Invoice Discount'):
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
def visualize_delivery_analysis1(data, delivery_status_col='Delivery Status'):
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

def visualize_delivery_analysis2(data, delivery_method_col='Delivery Methods'):
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

def visualize_payment_analysis(data, payment_status_col='Payment Status'):
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


# _________________Combined Analysis Function___________________________
def visualize_combined_analysis1(data, product_col='Product Name', 
                                 product_total_col='Product Total',  # Use item-level total
                                 qty_col='QTY',
                                 delivery_status_col='Delivery Status'):
    
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


def visualize_combined_analysis2(data, product_col='Product Name', 
                                delivery_status_col='Delivery Status'):

    # 1. Create a "Short Name" for the axis (e.g., first 15 chars + "...")
    def make_short_label(name, limit=22):
        s = str(name)
        return s[:limit] + '...' if len(s) > limit else s

    data['short_name'] = data[product_col].apply(make_short_label)

    # 2. Group Data: We group by both Full Name and Short Name to keep them linked
    #    This ensures we have the correct counts for the bars.
    counts = data.groupby([product_col, 'short_name', delivery_status_col]).size().reset_index(name='count')

    fig = go.Figure()

    # 3. Create the Bars
    for status in counts[delivery_status_col].unique():
        subset = counts[counts[delivery_status_col] == status]
        
        fig.add_trace(go.Bar(
            x=subset['short_name'],    # AXIS: Shows "Protein ba..."
            y=subset['count'],         # AXIS: Shows number
            name=status,
            # We pass the FULL name to customdata so the tooltip can use it
            customdata=subset[product_col],
            hovertemplate=(
                "<b>Product:</b> %{customdata}<br>" +  # Shows full long name
                "<b>Count:</b> %{y}<br>" +
                "<b>Status:</b> " + status + 
                "<extra></extra>" # Hides the secondary box
            )
        ))

    # 4. Layout Fixes
    fig.update_layout(
        xaxis_title="Product",
        yaxis_title="Number of Orders",
        barmode='group',
        template="plotly_white",
        xaxis=dict(
            tickangle=45,      # Rotate labels slightly
            automargin=True    # Key fix: allocates space so labels aren't cut off
        ),
        legend=dict(
            orientation="h",   # Horizontal legend at top
            yanchor="bottom", 
            y=1.02, 
            xanchor="right", 
            x=1
        )
    )

    st.plotly_chart(fig, use_container_width=True)


# _________________Velocity Analysis Function___________________________
def get_freq_alias(label):
    """Maps user-friendly labels to Pandas frequency aliases."""
    mapping = {
        "Daily": "D",
        "Weekly (Sun)": "W-SUN",
        "Monthly": "ME"
    }
    return mapping.get(label, "W-SUN")

# --- 1. Data Processing Functions (The "Logic") ---

def calculate_total_velocity(data, freq_label, date_col='Date Created', qty_col='QTY'):
    """Calculates total units sold based on frequency."""
    # Ensure date column is datetime
    data[date_col] = pd.to_datetime(data[date_col])
    freq_alias = get_freq_alias(freq_label)
    
    # Resample
    velocity_data = data[[date_col, qty_col]].copy()
    grouped_velocity = velocity_data.resample(freq_alias, on=date_col)[qty_col].sum().reset_index()
    
    # Rename for clarity
    grouped_velocity.rename(columns={date_col: 'Period', qty_col: 'Total Units Sold'}, inplace=True)
    
    return grouped_velocity

def calculate_store_velocity(data, freq_label, date_col='Date Created', qty_col='QTY', customer_col='Customer'):
    """Calculates units sold per store based on frequency."""
    data[date_col] = pd.to_datetime(data[date_col])
    freq_alias = get_freq_alias(freq_label)
    
    # Group by Customer AND Time Frequency
    store_velocity = data.groupby([
        customer_col, 
        pd.Grouper(key=date_col, freq=freq_alias)
    ])[qty_col].sum().reset_index()
    
    store_velocity.rename(columns={date_col: 'Period', qty_col: 'Units Sold'}, inplace=True)
    
    return store_velocity

# --- 2. Visualization Functions ---

def visualize_total_velocity(df_total, freq_label):
    """Visualizes the processed total velocity data."""
    fig = px.line(df_total, x='Period', y='Total Units Sold', markers=True)
    
    fig.update_traces(
        hovertemplate='<b>Units Sold:</b> %{y:.2f}<br><b>Period:</b> %{x}<extra></extra>'
    )

    fig.update_layout(
        title=f"Total Sales Velocity ({freq_label})",
        title_x=0.5,
        xaxis_title="Date",
        yaxis_title="Total Units Sold",
        height=400,
        hovermode="x unified",
        margin=dict(l=20, r=20, t=40, b=20)
    )
    st.plotly_chart(fig, use_container_width=True)

def visualize_store_velocity(df_store, freq_label, customer_col='Customer', qty_col='Units Sold'):
    """Visualizes the processed store velocity data."""
    # Identify Top 10 Stores for the view (based on total volume in the selected period)
    top_stores_series = df_store.groupby(customer_col)[qty_col].sum()
    top_stores = top_stores_series.nlargest(10).index.tolist()
    
    fig = px.line(
        df_store, 
        x='Period', 
        y=qty_col, 
        color=customer_col,
        markers=True,
    )
    fig.update_traces(
        hovertemplate='<b>Units Sold:</b> %{y:.2f}<br>'
        '<b>Period:</b> %{x|%Y-%m-%d}<br>'
        '<b>Customer:</b> %{fullData.name}<extra></extra>' 
    )

    # Show Top 10 by default
    fig.for_each_trace(lambda trace: trace.update(visible=True) if trace.name in top_stores else trace.update(visible='legendonly'))
    
    fig.update_layout(
        title=f"Store Sales Velocity ({freq_label})",
        title_x=0.5,
        xaxis_title="Date",
        yaxis_title="Units Sold",
        height=550, 
        margin=dict(l=20, r=20, t=40, b=20), 
        legend_title="Store Location",
        hovermode="x unified"
    )
    st.plotly_chart(fig, use_container_width=True)