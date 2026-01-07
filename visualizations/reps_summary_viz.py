import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import calendar
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

#Visualize the relationships between Orders/Cases Sold and Revenue
def plot_sales_relationships1(df):
    # Preprocess the data
    df = df.dropna(subset=["Orders Total", "Total Revenue"])
    df["Orders Total"] = pd.to_numeric(df["Orders Total"], errors='coerce')
    df["Total Revenue"] = pd.to_numeric(df["Total Revenue"], errors='coerce')
    df = df.dropna(subset=["Orders Total", "Total Revenue"])
    
    # Create the scatter plot
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["Orders Total"],
        y=df["Total Revenue"],
        mode='markers',
        marker=dict(color='LightSkyBlue', opacity=0.7),
        hovertemplate="<b>Orders Total: %{x}</b><br>Total Revenue: %{y}<extra></extra>"
    ))
    
    # Update layout with a title
    fig.update_layout(
        title="Relationship between Orders Total and Total Revenue",
        xaxis_title="Orders Total",
        yaxis_title="Total Revenue",
        template="plotly_white"
    )
    
    # Display in Streamlit
    st.plotly_chart(fig, use_container_width=True)


def plot_sales_relationships2(df):
    # Preprocess the data
    df = df.dropna(subset=["Cases Sold Total", "Total Revenue"])
    df["Cases Sold Total"] = pd.to_numeric(df["Cases Sold Total"], errors='coerce')
    df["Total Revenue"] = pd.to_numeric(df["Total Revenue"], errors='coerce')
    df = df.dropna(subset=["Cases Sold Total", "Total Revenue"])
    
    # Create the scatter plot
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["Cases Sold Total"],
        y=df["Total Revenue"],
        mode='markers',
        marker=dict(color='darkgreen', opacity=0.7),
        hovertemplate="<b>Cases Sold Total: %{x}</b><br>Total Revenue: %{y}<extra></extra>"
    ))
    
    # Update layout with a title
    fig.update_layout(
        title="Relationship between Cases Sold Total and Total Revenue",
        xaxis_title="Cases Sold Total",
        yaxis_title="Total Revenue",
        template="plotly_white"
    )
    
    # Display in Streamlit
    st.plotly_chart(fig, use_container_width=True)


#Revenue by Month and Role
def plot_revenue_by_month_and_role(df):
    # Convert 'Total Revenue' to numeric, coercing non-numeric values to NaN
    df['Total Revenue'] = pd.to_numeric(df['Total Revenue'], errors='coerce')
    
    # Convert 'Date' to datetime, coercing invalid dates to NaT
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df['Month'] = df['Date'].dt.month
    
    # Drop rows where 'Month' is NaN (invalid dates) or 'Role' is None
    df = df.dropna(subset=['Month'])
    df = df[df['Role'].notnull()]
    
    # Convert 'Month' to integer type to avoid float indices
    df['Month'] = df['Month'].astype(int)

    # Group by 'Month' and 'Role', sum 'Total Revenue'
    grouped_data = df.groupby(['Month', 'Role'])['Total Revenue'].sum().unstack(fill_value=0)
    
    # Create the figure
    fig = go.Figure()
    for role in grouped_data.columns:
        fig.add_trace(go.Bar(
            x=grouped_data.index,
            y=grouped_data[role],
            name=str(role),  # Convert role to string to avoid any issues
            text=grouped_data[role],
            texttemplate='%{text:.2s}',
            hovertemplate="<b>Month: %{x}</b><br>Role: " + str(role) + "<br>Total Revenue: %{y}<extra></extra>"
        ))
    
    # Update layout
    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Total Revenue",
        template="plotly_white",
        barmode='stack',
        legend_title="Role",
        coloraxis_colorbar=dict(title="Total Revenue"),
        xaxis=dict(
            tickmode='array',
            tickvals=grouped_data.index,
            ticktext=[calendar.month_name[m] for m in grouped_data.index]
        )
    )
    
    # Display the plot
    st.plotly_chart(fig, use_container_width=True)


#Visualize visits and travel distance for each name
def plot_visits_and_travel_distance_by_name(df):
    df = df.copy()
    if df['Travel Distance'].dtype == 'object':
         if df['Travel Distance'].str.contains(' mi').any():
             df['Travel Distance'] = pd.to_numeric(df['Travel Distance'].str.replace(' mi', ''), errors='coerce')
    
    grouped_data = df.groupby('Name')[['Visits', 'Travel Distance']].sum()

    fig = go.Figure()
    
    for column in grouped_data.columns:
        fig.add_trace(go.Bar(
            x=grouped_data.index,
            y=grouped_data[column],
            name=column,
            text=grouped_data[column].apply(lambda x: f'{x:.2f}'),
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>' +
                          f'{column}: ' + '%{y:.2f}' +
                          ('<br>Miles' if column == 'Travel distance' else '<br>Visits') +
                          '<extra></extra>'
        ))
    
    fig.update_layout(
        xaxis_title="Name",
        yaxis_title="Count / Distance",
        barmode='group',
        template="plotly_white",
        legend_title="Metrics",
        xaxis_tickangle=45,
        hoverlabel=dict(bgcolor="white", font_size=12)
    )
    
    st.plotly_chart(fig, use_container_width=True)

def plot_cases_sold_by_day_of_week(df):
    # Create a copy to avoid modifying the original DataFrame
    df = df.copy()
    
    # Convert 'Date' to datetime, coercing errors to NaT
    df['Day of Week'] = pd.to_datetime(df['Date'], errors='coerce').dt.dayofweek
    
    # Drop rows where 'Day of Week' is NaN (invalid dates)
    df = df.dropna(subset=['Day of Week'])
    
    # Ensure 'Day of Week' is integer type
    df['Day of Week'] = df['Day of Week'].astype(int)

    # Sum 'Cases Sold Total' by 'Day of Week' and include all days (0-6)
    cases_sold_by_day = df.groupby('Day of Week')['Cases Sold Total'].sum().reindex(range(7), fill_value=0)
    
    # Define day names
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    
    # Create the plot
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=cases_sold_by_day.index,
        y=cases_sold_by_day.values,
        mode='lines+markers',
        name='Cases Sold',
        line=dict(color='#636EFA', width=2),
        marker=dict(size=8, color='#636EFA'),
        hovertemplate='<b>%{text}</b><br>Cases Sold: %{y}<extra></extra>',
        text=[days[i] for i in cases_sold_by_day.index]
    ))
    
    fig.update_layout(
        title="Cases Sold by Day of the Week",
        xaxis_title="Day of the Week",
        yaxis_title="Cases Sold",
        template="plotly_white",
        xaxis=dict(
            tickmode='array',
            tickvals=list(range(7)),
            ticktext=days
        ),
        hovermode="x unified"
    )
    
    st.plotly_chart(fig, use_container_width=True)


def plot_revenue_trend_by_month_and_role(df):
    # Create a copy to avoid modifying the original DataFrame
    df = df.copy()

    # Convert 'Total Revenue' to numeric, coercing errors to NaN
    df['Total Revenue'] = pd.to_numeric(df['Total Revenue'], errors='coerce')
    
    # Convert 'Date' to datetime, coercing invalid dates to NaT
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    
    # Extract month period (e.g., '2022-01') for grouping
    df['Month'] = df['Date'].dt.to_period('M')

    # Drop rows with invalid 'Month', 'Role', or 'Total Revenue'
    df = df.dropna(subset=['Month', 'Role', 'Total Revenue'])

    # Group by 'Month' and 'Role', summing 'Total Revenue'
    monthly_revenue = df.groupby(['Month', 'Role'])['Total Revenue'].sum().unstack(fill_value=0)
    
    # Create the figure
    fig = go.Figure()
    
    # Add traces for each role
    for role in monthly_revenue.columns:
        fig.add_trace(go.Scatter(
            x=monthly_revenue.index.astype(str),  # Convert Period to string (e.g., '2022-01')
            y=monthly_revenue[role],
            mode='lines+markers',
            name=role,
            hovertemplate='<b>%{text}</b><br>' + role + ': $%{y:,.2f}<extra></extra>',
            text=[str(m) for m in monthly_revenue.index]  # Hover text shows 'YYYY-MM'
        ))
    
    # Update layout for clarity
    fig.update_layout(
        title="Revenue Trend by Month and Role",
        xaxis_title="Month (YYYY-MM)",
        yaxis_title="Total Revenue",
        template="plotly_white",
        xaxis=dict(
            tickmode='array',
            tickvals=monthly_revenue.index.astype(str),
            ticktext=[str(m) for m in monthly_revenue.index]  # X-axis shows 'YYYY-MM'
        ),
        hovermode="x unified",
        legend_title="Role"
    )
    
    # Display the plot in Streamlit
    st.plotly_chart(fig, use_container_width=True)

    
#Exploring the Relationship Between Visits and Orders
def plot_orders_vs_visits_with_regression(df):
    # Calculate the OLS trendline
    from scipy import stats
    df = df.copy()
    slope, intercept, r_value, p_value, std_err = stats.linregress(df['Visits'], df['Orders'])
    line = slope * df['Visits'] + intercept

    # Create the scatter plot
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df['Visits'],
        y=df['Orders'],
        mode='markers',
        name='Data Points',
        marker=dict(
            color='#636EFA',
            size=8
        ),
        hovertemplate='<b>Visits</b>: %{x}<br><b>Orders</b>: %{y}<extra></extra>'
    ))

    # Add the trendline
    fig.add_trace(go.Scatter(
        x=df['Visits'],
        y=line,
        mode='lines',
        name=f'Trendline (R²: {r_value**2:.3f})',
        line=dict(color='red', dash='dash'),
        hovertemplate='<b>Visits</b>: %{x}<br><b>Predicted Orders</b>: %{y:.2f}<extra></extra>'
    ))

    fig.update_layout(
        xaxis_title="Visits",
        yaxis_title="Orders",
        template="plotly_white",
        hovermode="closest",
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )

    st.plotly_chart(fig, use_container_width=True)

#Comparing Performance Metrics for Different Roles
def plot_multiple_metrics_by_role(df):
    df = df.copy()
    grouped_data = df.groupby('Role')[['Visits', 'Orders', 'Cases sold']].sum()

    fig = go.Figure()

    for column in grouped_data.columns:
        fig.add_trace(go.Bar(
            x=grouped_data.index,
            y=grouped_data[column],
            name=column,
            text=grouped_data[column].apply(lambda x: f'{x:.2f}'),
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>' + column + ': %{y:,.0f}<extra></extra>'
        ))

    fig.update_layout(
        xaxis_title="Role",
        yaxis_title="Count",
        barmode='group',
        template="plotly_white",
        legend_title="Metric",
        hovermode="closest"
    )

    st.plotly_chart(fig, use_container_width=True)

#Identifying Potential High-Value Clients
def plot_revenue_vs_cases_sold_with_size_and_color(df):
    df = df.copy()  # Create a copy of the DataFrame
    if df['Travel Distance'].dtype == 'object':
        if df['Travel Distance'].str.contains(' mi').any():
            df['Travel Distance'] = pd.to_numeric(df['Travel Distance'].str.replace(' mi', ''), errors='coerce')

    
    # Plotting with Plotly
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df["Cases sold"],
        y=df["Total Revenue"],
        mode='markers',
        marker=dict(
            size=df['Visits'],
            sizemode='area',
            sizeref=2.*max(df['Visits'])/(40.**2),
            color=df['Travel distance'],
            colorscale='Viridis',
            colorbar=dict(title="Travel distance"),
            opacity=0.7,
            showscale=True
        ),
        text=df.apply(lambda row: '<br>'.join([f'{col}: {row[col]}' for col in df.columns]), axis=1),
        hoverinfo='text'
    ))

    fig.update_layout(
        xaxis_title="Cases Sold",
        yaxis_title="Total Revenue",
        template="plotly_white",
        hovermode="closest"
    )

    st.plotly_chart(fig, use_container_width=True)


#__new____

def revenue_and_conversion_rate_comparison(df):
    data = df.copy()
    
    # Grouping the data by Name to calculate total revenue and conversion rate
    rep_data = data.groupby('Name').agg(
        total_revenue_direct=('Total Revenue (Direct)', 'sum'),
        total_revenue_3rd_party=('Total Revenue (3rd party)', 'sum'),
        total_revenue=('Total Revenue', 'sum'),
        total_visits=('Visits', 'sum'),
        total_orders=('Orders Total', 'sum')
    ).reset_index()

    # Calculating conversion rate as a percentage
    rep_data['conversion_rate'] = (rep_data['total_orders'] / rep_data['total_visits']) * 100

    # Create the figure
    fig = go.Figure()

    # Bar chart for total revenue by representative (Direct Sales)
    fig.add_trace(go.Bar(
        x=rep_data['Name'],
        y=rep_data['total_revenue_direct'],
        name='Total Revenue (Direct)',
        marker_color='rgb(26, 118, 255)',
        text=rep_data['total_revenue_direct'],
        textposition='auto'
    ))

    # Bar chart for total revenue by representative (3rd Party Sales)
    fig.add_trace(go.Bar(
        x=rep_data['Name'],
        y=rep_data['total_revenue_3rd_party'],
        name='Total Revenue (3rd Party)',
        marker_color='rgb(55, 83, 109)',
        text=rep_data['total_revenue_3rd_party'],
        textposition='auto'
    ))

    # Line chart for conversion rate by representative
    fig.add_trace(go.Scatter(
        x=rep_data['Name'],
        y=rep_data['conversion_rate'],
        name='Conversion Rate (%)',
        mode='lines+markers',
        marker=dict(color='rgb(255, 77, 77)', size=8),
        line=dict(color='rgb(255, 77, 77)', width=2),
        yaxis='y2'  # Create a secondary axis for the conversion rate
    ))

    # Update layout to include two y-axes
    fig.update_layout(
        xaxis_title='Representative',
        yaxis_title='Total Revenue (INR)',
        yaxis2=dict(
            title='Conversion Rate (%)',
            overlaying='y',
            side='right'
        ),
        barmode='group',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        template='plotly',
        xaxis_tickangle=-45  # Rotate the x-axis labels for readability
    )
    
    fig.update_traces(texttemplate='%{text:.2f}')
    st.plotly_chart(fig, use_container_width=True)

    """Summary of the Chart:
    - Total Revenue (Direct and 3rd Party) (Bar Chart): Displays the revenue generated by each representative through direct and 3rd party sales.
    - Conversion Rate (Line Chart): Shows the percentage of visits that resulted in orders, providing insight into the effectiveness of each representative.
    """

def revenue_conversion_and_trend(df):
    data = df.copy()

    # Ensuring 'Date' column is in datetime format
    data['Date'] = pd.to_datetime(data['Date'])

    # Grouping the data by Name to calculate total revenue and conversion rate
    rep_data = data.groupby('Name').agg(
        total_revenue_direct=('Total Revenue (Direct)', 'sum'),
        total_revenue_3rd_party=('Total Revenue (3rd party)', 'sum'),
        total_revenue=('Total Revenue', 'sum'),
        total_visits=('Visits', 'sum'),
        total_orders=('Orders Total', 'sum')
    ).reset_index()

    # Calculating conversion rate as a percentage
    rep_data['conversion_rate'] = (rep_data['total_orders'] / rep_data['total_visits']) * 100

    # Grouping by Date to calculate daily total revenue and orders
    date_data = data.groupby('Date').agg(
        daily_revenue=('Total Revenue', 'sum'),
        daily_orders=('Orders Total', 'sum'),
        daily_visits=('Visits', 'sum')
    ).reset_index()

    # Calculating daily conversion rate
    date_data['daily_conversion_rate'] = (date_data['daily_orders'] / date_data['daily_visits']) * 100

    # Now create a time-based figure for daily total revenue and conversion rate over time
    fig2 = go.Figure()

    # Line chart for daily total revenue
    fig2.add_trace(go.Scatter(
        x=date_data['Date'],
        y=date_data['daily_revenue'],
        name='Daily Revenue',
        mode='lines+markers',
        marker=dict(color='rgb(26, 118, 255)', size=8),
        line=dict(color='rgb(26, 118, 255)', width=2)
    ))

    # Line chart for daily conversion rate
    fig2.add_trace(go.Scatter(
        x=date_data['Date'],
        y=date_data['daily_conversion_rate'],
        name='Daily Conversion Rate (%)',
        mode='lines+markers',
        marker=dict(color='rgb(255, 77, 77)', size=8),
        line=dict(color='rgb(255, 77, 77)', width=2),
        yaxis='y2'  # Secondary axis for conversion rate
    ))

    # Update layout to include two y-axes
    fig2.update_layout(
        xaxis_title='Date',
        yaxis_title='Daily Revenue (INR)',
        yaxis2=dict(
            title='Daily Conversion Rate (%)',
            overlaying='y',
            side='right'
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        template='plotly'
    )

    st.plotly_chart(fig2, use_container_width=True)

    """Summary of the Charts:
    1. **Total Revenue and Conversion Rate by Representative**:
        - Shows total revenue from both direct and 3rd party sources per representative.
        - Conversion rate is calculated as the ratio of orders to visits.
    2. **Daily Trends**:
        - Shows daily revenue and conversion rate trends over time, helping to identify business performance patterns.
    """


def total_revenue_and_conversion_rate(df):
    data = df.copy()
    # Grouping the data by Representative to calculate total revenue and conversion rate
    rep_data = data.groupby('Name').agg(
        total_revenue=('Total Revenue', 'sum'),
        total_visits=('Visits', 'sum'),
        total_orders=('Orders Total', 'sum')
    ).reset_index()

    # Calculating conversion rate as a percentage
    rep_data['conversion_rate'] = (rep_data['total_orders'] / rep_data['total_visits']) * 100

    # Create the figure
    fig = go.Figure()

    # Bar chart for total revenue by representative
    fig.add_trace(go.Bar(
        x=rep_data['Name'],
        y=rep_data['total_revenue'],
        name='Total Revenue',
        marker_color='rgb(55, 83, 109)',
        text=rep_data['total_revenue'],
        textposition='auto'
    ))

    # Line chart for conversion rate by representative
    fig.add_trace(go.Scatter(
        x=rep_data['Name'],
        y=rep_data['conversion_rate'],
        name='Conversion Rate (%)',
        mode='lines+markers',
        marker=dict(color='rgb(255, 77, 77)', size=8),
        line=dict(color='rgb(255, 77, 77)', width=2),
        yaxis='y2'  # Create a secondary axis for the conversion rate
    ))

    # Update layout to include two y-axes
    fig.update_layout(
        xaxis_title='Representative',
        yaxis_title='Total Revenue (INR)',
        yaxis2=dict(
            title='Conversion Rate (%)',
            overlaying='y',
            side='right'
        ),
        barmode='group',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        template='plotly',
        xaxis_tickangle=-45  # Rotate the x-axis labels for readability
    )
    fig.update_traces(texttemplate='%{text:.2f}')
    st.plotly_chart(fig, use_container_width=True)

    """Summary of the Chart:
    Total Revenue (Bar Chart): This represents the revenue generated by each sales representative.
    Conversion Rate (Line Chart): This metric shows the percentage of visits that resulted in orders, indicating the effectiveness of each representative.
    """
    
def Total_Visits_vs_Total_Revenue(df):
    data = df.copy()
    # Grouping the data by Representative to calculate total revenue and conversion rate
    role_data = data.groupby('Role').agg(
        total_revenue=('Total Revenue', 'sum'),
        total_orders=('Orders Total', 'sum')
    ).reset_index()

    # Create the figure
    fig = go.Figure()

    # Bar chart for total revenue by role
    fig.add_trace(go.Bar(
        x=role_data['Role'],
        y=role_data['total_revenue'],
        name='Total Revenue',
        marker_color='rgb(55, 83, 109)',
        text=role_data['total_revenue'],
        textposition='auto'
    ))

    # Line chart for total orders by role
    fig.add_trace(go.Scatter(
        x=role_data['Role'],
        y=role_data['total_orders'],
        name='Total Orders',
        mode='lines+markers',
        marker=dict(color='rgb(255, 127, 80)', size=8),
        line=dict(color='rgb(255, 127, 80)', width=2),
        yaxis='y2'  # Secondary axis for total orders
    ))

    # Update layout to include two y-axes
    fig.update_layout(
        xaxis_title='Role',
        yaxis_title='Total Revenue',
        yaxis2=dict(
            title='Total Orders',
            overlaying='y',
            side='right'
        ),
        barmode='group',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        template='plotly',
        xaxis_tickangle=-45  # Rotate x-axis labels for better readability
    )


    fig.update_traces(texttemplate='%{text:.2f}')
    st.plotly_chart(fig, use_container_width=True)

