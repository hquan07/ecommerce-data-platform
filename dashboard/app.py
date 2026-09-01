import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import logging
from datetime import datetime, date

from dashboard.queries import (
    get_revenue_over_time,
    get_revenue_by_category,
    get_order_status_breakdown,
    get_delivery_time_distribution,
    get_customer_count_by_state,
    get_payment_methods,
    get_top_products,
    get_review_score_distribution,
    get_customer_segments,
    get_segment_scatter
)

logging.basicConfig(level=logging.INFO)

app = dash.Dash(__name__, title="E-commerce Dashboard", external_stylesheets=[dbc.themes.FLATLY, "https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap"])

# Fetch states for dropdown once at startup
try:
    df_states_init = get_customer_count_by_state()
    state_options = [{'label': 'All States', 'value': 'ALL'}] + [{'label': s, 'value': s} for s in df_states_init['customer_state'].dropna().unique()]
except Exception as e:
    logging.error(f"Error fetching states: {e}")
    state_options = [{'label': 'All States', 'value': 'ALL'}]

app.layout = dbc.Container([
    html.Div(style={"height": "30px"}),
    html.H1("🛒 E-Commerce Data Platform", className="text-center mb-4 fade-in-slide-up", style={"fontWeight": "800", "background": "-webkit-linear-gradient(45deg, #667eea, #764ba2)", "-webkit-background-clip": "text", "-webkit-text-fill-color": "transparent"}),
    
    # Filters Row
    dbc.Row([
        dbc.Col([
            html.Label("Date Range:", className="fw-bold"),
            dcc.DatePickerRange(
                id='date-picker-range',
                min_date_allowed=date(2016, 1, 1),
                max_date_allowed=date(2026, 12, 31),
                initial_visible_month=date(2018, 8, 1),
                start_date=date(2017, 1, 1),
                end_date=date(2018, 12, 31),
                className="mb-3",
                style={"width": "100%"}
            )
        ], width=4),
        dbc.Col([
            html.Label("Customer State:", className="fw-bold"),
            dcc.Dropdown(
                id='state-dropdown',
                options=state_options,
                value='ALL',
                clearable=False,
                className="mb-3"
            )
        ], width=4),
    ], className="mb-4 justify-content-center fade-in-slide-up", style={"position": "relative", "zIndex": 999}),
    
    # KPI Cards Row (will be updated via callback)
    dbc.Row(id='kpi-row', className="mb-5 justify-content-center"),

    # Tabs
    dbc.Tabs([
        dbc.Tab(label="💰 Sales & Revenue", children=[
            html.Br(),
            dbc.Row([dbc.Col(dcc.Loading(dcc.Graph(id='fig_rev_time', className="dash-graph")), width=12)]),
            html.Br(),
            dbc.Row([
                dbc.Col(dcc.Loading(dcc.Graph(id='fig_rev_cat', className="dash-graph")), width=7),
                dbc.Col(dcc.Loading(dcc.Graph(id='fig_payment', className="dash-graph")), width=5)
            ])
        ], className="fade-in-slide-up"),
        
        dbc.Tab(label="📦 Orders & Operations", children=[
            html.Br(),
            dbc.Row([
                dbc.Col(dcc.Loading(dcc.Graph(id='fig_order_status', className="dash-graph")), width=5),
                dbc.Col(dcc.Loading(dcc.Graph(id='fig_delivery', className="dash-graph")), width=7)
            ])
        ], className="fade-in-slide-up"),
        
        dbc.Tab(label="👥 Customers", children=[
            html.Br(),
            dbc.Row([dbc.Col(dcc.Loading(dcc.Graph(id='fig_customer', className="dash-graph")), width=12)])
        ], className="fade-in-slide-up"),
        
        dbc.Tab(label="🏷️ Products & Reviews", children=[
            html.Br(),
            dbc.Row([
                dbc.Col(dcc.Loading(dcc.Graph(id='fig_products', className="dash-graph")), width=6),
                dbc.Col(dcc.Loading(dcc.Graph(id='fig_reviews', className="dash-graph")), width=6)
            ])
        ], className="fade-in-slide-up"),
        
        dbc.Tab(label="🤖 ML Customer Segments", children=[
            html.Br(),
            dbc.Row([
                dbc.Col(dcc.Loading(dcc.Graph(id='fig_ml_treemap', className="dash-graph")), width=6),
                dbc.Col(dcc.Loading(dcc.Graph(id='fig_ml_radar', className="dash-graph")), width=6)
            ], className="mb-4"),
            dbc.Row([
                dbc.Col(dcc.Loading(dcc.Graph(id='fig_ml_scatter_3d', className="dash-graph")), width=6),
                dbc.Col(dcc.Loading(dcc.Graph(id='fig_ml_box', className="dash-graph")), width=6)
            ])
        ], className="fade-in-slide-up"),
    ])
], fluid=True, className="dashboard-container")

@app.callback(
    [
        Output('kpi-row', 'children'),
        Output('fig_rev_time', 'figure'),
        Output('fig_rev_cat', 'figure'),
        Output('fig_payment', 'figure'),
        Output('fig_order_status', 'figure'),
        Output('fig_delivery', 'figure'),
        Output('fig_customer', 'figure'),
        Output('fig_products', 'figure'),
        Output('fig_reviews', 'figure'),
        Output('fig_ml_treemap', 'figure'),
        Output('fig_ml_radar', 'figure'),
        Output('fig_ml_scatter_3d', 'figure'),
        Output('fig_ml_box', 'figure')
    ],
    [
        Input('date-picker-range', 'start_date'),
        Input('date-picker-range', 'end_date'),
        Input('state-dropdown', 'value')
    ]
)
def update_dashboard(start_date, end_date, state):
    try:
        # Fetch filtered data
        df_revenue_time = get_revenue_over_time(start_date, end_date, state)
        df_revenue_cat = get_revenue_by_category(start_date, end_date, state)
        df_order_status = get_order_status_breakdown(start_date, end_date, state)
        df_delivery = get_delivery_time_distribution(start_date, end_date, state)
        df_customer = get_customer_count_by_state(start_date, end_date)
        df_payment = get_payment_methods(start_date, end_date, state)
        df_products = get_top_products(start_date, end_date, state)
        
        # Will return empty if table doesn't exist
        df_reviews = get_review_score_distribution(start_date, end_date, state)
        
        # ML data (not filtered by date typically as segments are based on lifetime)
        df_segments = get_customer_segments()
        df_scatter = get_segment_scatter()

        # Build KPIs
        total_cust = df_customer['customer_count'].sum() if not df_customer.empty else 0
        total_rev = df_revenue_time['total_revenue'].sum() if not df_revenue_time.empty else 0
        total_ord = df_order_status['order_count'].sum() if not df_order_status.empty else 0
        
        kpi_row = [
            dbc.Col(dbc.Card([dbc.CardBody([html.H5("Filtered Customers", className="card-title fw-bold opacity-75"), html.H2(f"{total_cust}", className="fw-bold m-0")])], className="kpi-card gradient-blue fade-in-slide-up"), width=4),
            dbc.Col(dbc.Card([dbc.CardBody([html.H5("Filtered Revenue", className="card-title fw-bold opacity-75"), html.H2(f"${total_rev:,.0f}", className="fw-bold m-0")])], className="kpi-card gradient-green fade-in-slide-up"), width=4),
            dbc.Col(dbc.Card([dbc.CardBody([html.H5("Filtered Orders", className="card-title fw-bold opacity-75"), html.H2(f"{total_ord}", className="fw-bold m-0")])], className="kpi-card gradient-orange fade-in-slide-up"), width=4),
        ]

        # Build Figures
        empty_fig = px.bar(title="No Data")
        empty_fig.update_layout(template="plotly_white")

        fig_rev_time = px.area(df_revenue_time, x="month", y="total_revenue", title="Revenue Over Time", template="plotly_white") if not df_revenue_time.empty else empty_fig
        fig_rev_cat = px.bar(df_revenue_cat, x="product_category_name_english", y="total_revenue", title="Top 10 Categories by Revenue", template="plotly_white") if not df_revenue_cat.empty else empty_fig
        fig_payment = px.pie(df_payment, names="payment_type", values="usage_count", title="Payment Methods", template="plotly_white", hole=0.4) if not df_payment.empty else empty_fig
        
        fig_order_status = px.pie(df_order_status, names="order_status", values="order_count", title="Order Status", hole=0.3, template="plotly_white") if not df_order_status.empty else empty_fig
        fig_delivery = px.histogram(df_delivery, x="delivery_days", nbins=50, title="Delivery Time (Days)", template="plotly_white") if not df_delivery.empty else empty_fig
        
        fig_customer = px.bar(df_customer, x="customer_state", y="customer_count", title="Customers by State", color="customer_count", template="plotly_white") if not df_customer.empty else empty_fig
        fig_products = px.bar(df_products, x="product_category_name_english", y="items_sold", title="Top 10 Categories", template="plotly_white") if not df_products.empty else empty_fig
        
        if not df_reviews.empty:
            fig_reviews = px.bar(df_reviews, x="review_score", y="review_count", title="Review Score", template="plotly_white")
            fig_reviews.update_xaxes(type='category')
        else:
            fig_reviews = empty_fig

        # ML Figures
        if not df_segments.empty:
            # 1. Treemap (Size vs Monetary)
            fig_ml_treemap = px.treemap(df_segments, path=[px.Constant("All Segments"), "segment_name"], values="customer_count",
                                        color="avg_monetary", color_continuous_scale="Blues",
                                        title="Segment Size & Avg Revenue (Treemap)", template="plotly_white")
            
            # 2. Radar Chart (Normalized Profiles)
            fig_ml_radar = go.Figure()
            for col in ['avg_recency', 'avg_frequency', 'avg_monetary']:
                max_val = df_segments[col].max()
                df_segments[f'{col}_norm'] = df_segments[col] / max_val if max_val > 0 else 0
                
            categories = ['Recency', 'Frequency', 'Monetary']
            colors = px.colors.qualitative.Plotly
            for i, row in df_segments.iterrows():
                fig_ml_radar.add_trace(go.Scatterpolar(
                    r=[row['avg_recency_norm'], row['avg_frequency_norm'], row['avg_monetary_norm']],
                    theta=categories,
                    fill='toself',
                    name=row['segment_name'],
                    line_color=colors[i % len(colors)]
                ))
            fig_ml_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 1])), 
                                       title="Segment Profiles (Normalized RFM)", template="plotly_white")
        else:
            fig_ml_treemap = px.bar(title="Run ML Pipeline First")
            fig_ml_radar = px.bar(title="Run ML Pipeline First")
            
        if not df_scatter.empty:
            # 3. 3D Scatter Plot
            fig_ml_scatter_3d = px.scatter_3d(df_scatter, x="recency", y="frequency", z="monetary", color="segment_name", 
                                        title="3D RFM Clusters", template="plotly_white")
            fig_ml_scatter_3d.update_traces(marker=dict(size=3))
            
            # 4. Box Plot (Monetary Distribution)
            fig_ml_box = px.box(df_scatter, x="segment_name", y="monetary", color="segment_name", 
                                title="Monetary Distribution (Log Scale)", template="plotly_white", log_y=True)
        else:
            fig_ml_scatter_3d = px.scatter(title="Run ML Pipeline First")
            fig_ml_box = px.bar(title="Run ML Pipeline First")

        return (
            kpi_row, 
            fig_rev_time, fig_rev_cat, fig_payment, 
            fig_order_status, fig_delivery, 
            fig_customer, 
            fig_products, fig_reviews,
            fig_ml_treemap, fig_ml_radar, fig_ml_scatter_3d, fig_ml_box
        )
    except Exception as e:
        logging.error(f"Dashboard update error: {e}")
        empty_fig = px.bar(title="Error Loading Data")
        return [html.Div("Error", className="text-danger")] + [empty_fig]*12

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8050, debug=True)
