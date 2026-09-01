import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import logging
from dashboard.queries import (
    get_revenue_over_time,
    get_revenue_by_category,
    get_order_status_breakdown,
    get_delivery_time_distribution,
    get_customer_count_by_state,
    get_payment_methods,
    get_top_products,
    get_review_score_distribution
)

logging.basicConfig(level=logging.INFO)

# Initialize with a Bootstrap theme and load external font
app = dash.Dash(__name__, title="E-commerce Dashboard", external_stylesheets=[dbc.themes.FLATLY, "https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap"])

def serve_layout():
    try:
        # 1. Fetch all data
        df_revenue_time = get_revenue_over_time()
        df_revenue_cat = get_revenue_by_category()
        df_order_status = get_order_status_breakdown()
        df_delivery = get_delivery_time_distribution()
        df_customer = get_customer_count_by_state()
        df_payment = get_payment_methods()
        df_products = get_top_products()
        df_reviews = get_review_score_distribution()

        # 2. Create Figures
        # --- Tab 1: Sales & Revenue ---
        if not df_revenue_time.empty:
            fig_rev_time = px.area(df_revenue_time, x="month", y="total_revenue", title="Revenue Over Time", template="plotly_white")
        else:
            fig_rev_time = px.area(title="No Data")

        if not df_revenue_cat.empty:
            fig_rev_cat = px.bar(df_revenue_cat, x="product_category_name_english", y="total_revenue", title="Top 10 Categories by Revenue", template="plotly_white")
        else:
            fig_rev_cat = px.bar(title="No Data")
            
        if not df_payment.empty:
            fig_payment = px.pie(df_payment, names="payment_type", values="usage_count", title="Payment Methods Breakdown", template="plotly_white", hole=0.4)
        else:
            fig_payment = px.pie(title="No Data")

        # --- Tab 2: Orders & Operations ---
        if not df_order_status.empty:
            fig_order_status = px.pie(df_order_status, names="order_status", values="order_count", title="Order Status Breakdown", hole=0.3, template="plotly_white")
        else:
            fig_order_status = px.pie(title="No Data")

        if not df_delivery.empty:
            fig_delivery = px.histogram(df_delivery, x="delivery_days", nbins=50, title="Delivery Time Distribution (Days)", template="plotly_white")
        else:
            fig_delivery = px.histogram(title="No Data")

        # --- Tab 3: Customers ---
        if not df_customer.empty:
            fig_customer = px.bar(df_customer, x="customer_state", y="customer_count", title="Customers by State", color="customer_count", template="plotly_white")
        else:
            fig_customer = px.bar(title="No Data")

        # --- Tab 4: Products & Reviews ---
        if not df_products.empty:
            fig_products = px.bar(df_products, x="product_category_name_english", y="items_sold", title="Top 10 Best-Selling Categories", template="plotly_white")
        else:
            fig_products = px.bar(title="No Data")

        if not df_reviews.empty:
            fig_reviews = px.bar(df_reviews, x="review_score", y="review_count", title="Review Score Distribution", template="plotly_white")
            fig_reviews.update_xaxes(type='category')
        else:
            fig_reviews = px.bar(title="No Data")

        # 3. Layout Structure
        return dbc.Container([
            html.Div(style={"height": "30px"}),
            html.H1("🛒 E-Commerce Data Platform", className="text-center mb-4 fade-in-slide-up", style={"fontWeight": "800", "background": "-webkit-linear-gradient(45deg, #667eea, #764ba2)", "-webkit-background-clip": "text", "-webkit-text-fill-color": "transparent"}),
            
            # KPI Cards
            dbc.Row([
                dbc.Col(dbc.Card([dbc.CardBody([html.H5("Total Customers", className="card-title fw-bold opacity-75"), html.H2(f"{df_customer['customer_count'].sum() if not df_customer.empty else 0}", className="fw-bold m-0")])], className="kpi-card gradient-blue fade-in-slide-up"), width=4),
                dbc.Col(dbc.Card([dbc.CardBody([html.H5("Total Revenue", className="card-title fw-bold opacity-75"), html.H2(f"${df_revenue_time['total_revenue'].sum():,.0f}" if not df_revenue_time.empty else "$0", className="fw-bold m-0")])], className="kpi-card gradient-green fade-in-slide-up", style={"animationDelay": "0.1s"}), width=4),
                dbc.Col(dbc.Card([dbc.CardBody([html.H5("Total Orders", className="card-title fw-bold opacity-75"), html.H2(f"{df_order_status['order_count'].sum() if not df_order_status.empty else 0}", className="fw-bold m-0")])], className="kpi-card gradient-orange fade-in-slide-up", style={"animationDelay": "0.2s"}), width=4),
            ], className="mb-5 mt-4 justify-content-center"),

            # Tabs for different charts
            dbc.Tabs([
                dbc.Tab(label="💰 Sales & Revenue", children=[
                    html.Br(),
                    dbc.Row([dbc.Col(html.Div(dcc.Graph(figure=fig_rev_time), className="dash-graph"), width=12)]),
                    html.Br(),
                    dbc.Row([
                        dbc.Col(html.Div(dcc.Graph(figure=fig_rev_cat), className="dash-graph"), width=7),
                        dbc.Col(html.Div(dcc.Graph(figure=fig_payment), className="dash-graph"), width=5)
                    ])
                ], className="fade-in-slide-up", style={"animationDelay": "0.3s"}),
                dbc.Tab(label="📦 Orders & Operations", children=[
                    html.Br(),
                    dbc.Row([
                        dbc.Col(html.Div(dcc.Graph(figure=fig_order_status), className="dash-graph"), width=5),
                        dbc.Col(html.Div(dcc.Graph(figure=fig_delivery), className="dash-graph"), width=7)
                    ])
                ], className="fade-in-slide-up", style={"animationDelay": "0.3s"}),
                dbc.Tab(label="👥 Customers", children=[
                    html.Br(),
                    dbc.Row([dbc.Col(html.Div(dcc.Graph(figure=fig_customer), className="dash-graph"), width=12)])
                ], className="fade-in-slide-up", style={"animationDelay": "0.3s"}),
                dbc.Tab(label="🏷️ Products & Reviews", children=[
                    html.Br(),
                    dbc.Row([
                        dbc.Col(html.Div(dcc.Graph(figure=fig_products), className="dash-graph"), width=6),
                        dbc.Col(html.Div(dcc.Graph(figure=fig_reviews), className="dash-graph"), width=6)
                    ])
                ], className="fade-in-slide-up", style={"animationDelay": "0.3s"}),
            ])
        ], fluid=True, className="dashboard-container")

    except Exception as e:
        logging.error(f"Error loading dashboard layout: {e}")
        return dbc.Container([
            html.H1("E-Commerce Dashboard", className="mt-5 text-center text-danger"),
            html.P("Error loading data from Data Warehouse. Please check the logs.", className="text-center")
        ])

app.layout = serve_layout

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8050, debug=True)
