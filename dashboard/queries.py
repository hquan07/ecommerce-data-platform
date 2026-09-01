import os
import psycopg2
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "postgres"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        dbname=os.getenv("POSTGRES_DB", "ecommerce"),
        user=os.getenv("POSTGRES_USER", "ecommerce"),
        password=os.getenv("POSTGRES_PASSWORD", "ecommerce")
    )

def fetch_data(query):
    try:
        conn = get_db_connection()
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        logger.error(f"Failed to fetch data: {e}")
        return pd.DataFrame()

# 1. Sales & Revenue Queries
def get_revenue_over_time():
    query = """
    SELECT date_trunc('month', o.order_purchase_timestamp) as month, SUM(p.payment_value) as total_revenue
    FROM dw.fact_orders o
    JOIN dw.fact_payments p ON o.order_id = p.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY month
    ORDER BY month;
    """
    return fetch_data(query)

def get_revenue_by_category():
    query = """
    SELECT pr.product_category_name_english, SUM(oi.price) as total_revenue
    FROM dw.fact_order_items oi
    JOIN dw.dim_product pr ON oi.product_id = pr.product_id
    JOIN dw.fact_orders o ON oi.order_id = o.order_id
    WHERE o.order_status = 'delivered' AND pr.product_category_name_english IS NOT NULL
    GROUP BY pr.product_category_name_english
    ORDER BY total_revenue DESC
    LIMIT 10;
    """
    return fetch_data(query)

# 2. Orders & Operations Queries
def get_order_status_breakdown():
    query = """
    SELECT order_status, COUNT(*) as order_count
    FROM dw.fact_order
    GROUP BY order_status
    ORDER BY order_count DESC;
    """
    return fetch_data(query)

def get_delivery_time_distribution():
    query = """
    SELECT 
        EXTRACT(EPOCH FROM (order_delivered_customer_date - order_purchase_timestamp))/86400 as delivery_days
    FROM dw.fact_order
    WHERE order_status = 'delivered' AND order_delivered_customer_date IS NOT NULL
    """
    return fetch_data(query)

# 3. Customer Queries
def get_customer_count_by_state():
    query = """
    SELECT customer_state, COUNT(DISTINCT customer_unique_id) as customer_count
    FROM dw.dim_customer
    GROUP BY customer_state
    ORDER BY customer_count DESC;
    """
    return fetch_data(query)

def get_payment_methods():
    query = """
    SELECT payment_type, COUNT(*) as usage_count
    FROM dw.fact_payments
    GROUP BY payment_type
    ORDER BY usage_count DESC;
    """
    return fetch_data(query)

# 4. Products & Sellers Queries
def get_top_products():
    query = """
    SELECT pr.product_category_name_english, COUNT(oi.product_id) as items_sold
    FROM dw.fact_order_items oi
    JOIN dw.dim_product pr ON oi.product_id = pr.product_id
    WHERE pr.product_category_name_english IS NOT NULL
    GROUP BY pr.product_category_name_english
    ORDER BY items_sold DESC
    LIMIT 10;
    """
    return fetch_data(query)

def get_review_score_distribution():
    query = """
    SELECT review_score, COUNT(*) as review_count
    FROM dw.fact_reviews
    GROUP BY review_score
    ORDER BY review_score DESC;
    """
    return fetch_data(query)
