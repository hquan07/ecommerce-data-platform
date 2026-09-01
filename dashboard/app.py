import dash
from dash import dcc, html
import plotly.express as px
from dashboard.queries import get_customer_count_by_state
import logging

logging.basicConfig(level=logging.INFO)

app = dash.Dash(__name__, title="E-commerce Dashboard")

def serve_layout():
    try:
        df = get_customer_count_by_state()
        
        if df.empty:
            fig = px.bar(title="No Data Available in Data Warehouse")
        else:
            fig = px.bar(
                df, 
                x="customer_state", 
                y="customer_count", 
                title="Customers by State",
                labels={"customer_state": "State", "customer_count": "Number of Customers"},
                color="customer_count",
                template="plotly_white"
            )
            
        return html.Div(
            style={"fontFamily": "Segoe UI, Tahoma, Geneva, Verdana, sans-serif", "padding": "40px", "backgroundColor": "#f8f9fa", "minHeight": "100vh"},
            children=[
                html.Div(
                    style={"backgroundColor": "white", "padding": "30px", "borderRadius": "10px", "boxShadow": "0 4px 6px rgba(0,0,0,0.1)"},
                    children=[
                        html.H1("🛒 E-Commerce Data Platform Dashboard", style={"textAlign": "center", "color": "#2c3e50", "marginBottom": "30px"}),
                        html.Hr(style={"borderColor": "#e9ecef", "marginBottom": "30px"}),
                        html.Div(
                            style={"display": "flex", "justifyContent": "space-around", "marginBottom": "40px"},
                            children=[
                                html.Div(
                                    style={"textAlign": "center", "padding": "20px", "backgroundColor": "#e3f2fd", "borderRadius": "8px", "width": "30%"},
                                    children=[
                                        html.H3("Total Customers", style={"color": "#1565c0", "margin": "0"}),
                                        html.H2(f"{df['customer_count'].sum() if not df.empty else 0}", style={"fontSize": "48px", "margin": "10px 0"})
                                    ]
                                )
                            ]
                        ),
                        html.Div([
                            html.H3("Customer Demographics", style={"color": "#34495e"}),
                            dcc.Graph(figure=fig)
                        ])
                    ]
                )
            ]
        )
    except Exception as e:
        logging.error(f"Error loading dashboard layout: {e}")
        return html.Div(
            style={"padding": "40px", "textAlign": "center"},
            children=[
                html.H1("E-Commerce Dashboard"),
                html.P("Error loading data from Data Warehouse. Please check the logs.")
            ]
        )

app.layout = serve_layout

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8050, debug=True)
