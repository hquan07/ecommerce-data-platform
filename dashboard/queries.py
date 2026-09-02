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

def fetch_data(query, params=None):
    try:
        conn = get_db_connection()
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        return df
    except Exception as e:
        logger.error(f"Failed to fetch data: {e}")
        return pd.DataFrame()

def build_where_clause(start_date=None, end_date=None, state='ALL', time_col='o.order_purchase_timestamp', state_col='c.customer_state'):
    conditions = []
    params = {}
    
    if start_date:
        conditions.append(f"{time_col} >= %(start_date)s")
        params['start_date'] = start_date
    if end_date:
        conditions.append(f"{time_col} <= %(end_date)s")
        params['end_date'] = end_date
    if state and state != 'ALL':
        conditions.append(f"{state_col} = %(state)s")
        params['state'] = state
        
    where_str = " AND ".join(conditions)
    if where_str:
        where_str = " AND " + where_str
    
    return where_str, params

# 1. Sales & Revenue Queries
def get_revenue_over_time(start_date=None, end_date=None, state='ALL'):
    where_clause, params = build_where_clause(start_date, end_date, state)
    query = f"""
    SELECT date_trunc('month', o.order_purchase_timestamp) as month, SUM(p.payment_value) as total_revenue
    FROM dw.fact_orders o
    JOIN dw.fact_payments p ON o.order_id = p.order_id
    JOIN dw.dim_customer c ON o.customer_id = c.customer_id
    WHERE o.order_status = 'delivered' {where_clause}
    GROUP BY month
    ORDER BY month;
    """
    return fetch_data(query, params)

def get_revenue_by_category(start_date=None, end_date=None, state='ALL'):
    where_clause, params = build_where_clause(start_date, end_date, state)
    query = f"""
    SELECT pr.product_category_name_english, SUM(oi.price) as total_revenue
    FROM dw.fact_order_items oi
    JOIN dw.dim_product pr ON oi.product_id = pr.product_id
    JOIN dw.fact_orders o ON oi.order_id = o.order_id
    JOIN dw.dim_customer c ON o.customer_id = c.customer_id
    WHERE o.order_status = 'delivered' AND pr.product_category_name_english IS NOT NULL {where_clause}
    GROUP BY pr.product_category_name_english
    ORDER BY total_revenue DESC
    LIMIT 10;
    """
    return fetch_data(query, params)

# 2. Orders & Operations Queries
def get_order_status_breakdown(start_date=None, end_date=None, state='ALL'):
    where_clause, params = build_where_clause(start_date, end_date, state)
    # Remove the starting ' AND ' if there's no preceding condition in WHERE
    where_clean = where_clause.replace(" AND ", "", 1) if where_clause else ""
    where_final = f"WHERE {where_clean}" if where_clean else ""
    
    # Previous code queried dw.fact_order, let's fix to dw.fact_orders
    query = f"""
    SELECT o.order_status, COUNT(*) as order_count
    FROM dw.fact_orders o
    JOIN dw.dim_customer c ON o.customer_id = c.customer_id
    {where_final}
    GROUP BY o.order_status
    ORDER BY order_count DESC;
    """
    return fetch_data(query, params)

def get_delivery_time_distribution(start_date=None, end_date=None, state='ALL'):
    where_clause, params = build_where_clause(start_date, end_date, state)
    query = f"""
    SELECT 
        EXTRACT(EPOCH FROM (o.order_delivered_customer_date - o.order_purchase_timestamp))/86400 as delivery_days
    FROM dw.fact_orders o
    JOIN dw.dim_customer c ON o.customer_id = c.customer_id
    WHERE o.order_status = 'delivered' AND o.order_delivered_customer_date IS NOT NULL {where_clause}
    """
    return fetch_data(query, params)

# 3. Customer Queries
def get_customer_count_by_state(start_date=None, end_date=None):
    where_clause, params = build_where_clause(start_date, end_date, state='ALL')
    
    query = f"""
    SELECT c.customer_state, COUNT(DISTINCT c.customer_unique_id) as customer_count
    FROM dw.dim_customer c
    JOIN dw.fact_orders o ON c.customer_id = o.customer_id
    WHERE 1=1 {where_clause}
    GROUP BY c.customer_state
    ORDER BY customer_count DESC;
    """
    return fetch_data(query, params)

def get_payment_methods(start_date=None, end_date=None, state='ALL'):
    where_clause, params = build_where_clause(start_date, end_date, state)
    
    query = f"""
    SELECT p.payment_type, COUNT(*) as usage_count
    FROM dw.fact_payments p
    JOIN dw.fact_orders o ON p.order_id = o.order_id
    JOIN dw.dim_customer c ON o.customer_id = c.customer_id
    WHERE 1=1 {where_clause}
    GROUP BY p.payment_type
    ORDER BY usage_count DESC;
    """
    return fetch_data(query, params)

# 4. Products & Sellers Queries
def get_top_products(start_date=None, end_date=None, state='ALL'):
    where_clause, params = build_where_clause(start_date, end_date, state)
    
    query = f"""
    SELECT pr.product_category_name_english, COUNT(oi.product_id) as items_sold
    FROM dw.fact_order_items oi
    JOIN dw.dim_product pr ON oi.product_id = pr.product_id
    JOIN dw.fact_orders o ON oi.order_id = o.order_id
    JOIN dw.dim_customer c ON o.customer_id = c.customer_id
    WHERE pr.product_category_name_english IS NOT NULL {where_clause}
    GROUP BY pr.product_category_name_english
    ORDER BY items_sold DESC
    LIMIT 10;
    """
    return fetch_data(query, params)

def get_review_score_distribution(start_date=None, end_date=None, state='ALL'):
    where_clause, params = build_where_clause(start_date, end_date, state)
    
    query = f"""
    SELECT r.review_score, COUNT(*) as review_count
    FROM dw.fact_reviews r
    JOIN dw.fact_orders o ON r.order_id = o.order_id
    JOIN dw.dim_customer c ON o.customer_id = c.customer_id
    WHERE 1=1 {where_clause}
    GROUP BY r.review_score
    ORDER BY r.review_score DESC;
    """
    return fetch_data(query, params)

# --- New Charts Queries ---

# Orders & Operations: Order Heatmap (hour × day of week)
def get_order_heatmap(start_date=None, end_date=None, state='ALL'):
    where_clause, params = build_where_clause(start_date, end_date, state)
    query = f"""
    SELECT
        EXTRACT(DOW FROM o.order_purchase_timestamp)::int as day_of_week,
        EXTRACT(HOUR FROM o.order_purchase_timestamp)::int as hour_of_day,
        COUNT(*) as order_count
    FROM dw.fact_orders o
    JOIN dw.dim_customer c ON o.customer_id = c.customer_id
    WHERE 1=1 {where_clause}
    GROUP BY day_of_week, hour_of_day
    ORDER BY day_of_week, hour_of_day;
    """
    return fetch_data(query, params)

# Orders & Operations: Late Delivery Rate by month
def get_late_delivery_rate(start_date=None, end_date=None, state='ALL'):
    where_clause, params = build_where_clause(start_date, end_date, state)
    query = f"""
    SELECT
        date_trunc('month', o.order_purchase_timestamp) as month,
        COUNT(*) as total_delivered,
        SUM(CASE WHEN o.order_delivered_customer_date > o.order_estimated_delivery_date THEN 1 ELSE 0 END) as late_count,
        ROUND(
            100.0 * SUM(CASE WHEN o.order_delivered_customer_date > o.order_estimated_delivery_date THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0),
            2
        ) as late_rate_pct
    FROM dw.fact_orders o
    JOIN dw.dim_customer c ON o.customer_id = c.customer_id
    WHERE o.order_status = 'delivered'
      AND o.order_delivered_customer_date IS NOT NULL
      AND o.order_estimated_delivery_date IS NOT NULL
      {where_clause}
    GROUP BY month
    ORDER BY month;
    """
    return fetch_data(query, params)

# Customers: Retention (one-time vs repeat)
def get_customer_retention(start_date=None, end_date=None, state='ALL'):
    where_clause, params = build_where_clause(start_date, end_date, state)
    query = f"""
    SELECT
        CASE WHEN order_cnt = 1 THEN 'One-time' ELSE 'Repeat' END as customer_type,
        COUNT(*) as customer_count
    FROM (
        SELECT c.customer_unique_id, COUNT(DISTINCT o.order_id) as order_cnt
        FROM dw.dim_customer c
        JOIN dw.fact_orders o ON c.customer_id = o.customer_id
        WHERE 1=1 {where_clause}
        GROUP BY c.customer_unique_id
    ) sub
    GROUP BY customer_type;
    """
    return fetch_data(query, params)

# Customers: New Customers Over Time
def get_new_customers_over_time(start_date=None, end_date=None, state='ALL'):
    where_clause, params = build_where_clause(start_date, end_date, state)
    query = f"""
    SELECT
        date_trunc('month', first_order) as month,
        COUNT(*) as new_customers
    FROM (
        SELECT c.customer_unique_id, MIN(o.order_purchase_timestamp) as first_order
        FROM dw.dim_customer c
        JOIN dw.fact_orders o ON c.customer_id = o.customer_id
        WHERE 1=1 {where_clause}
        GROUP BY c.customer_unique_id
    ) sub
    GROUP BY month
    ORDER BY month;
    """
    return fetch_data(query, params)

# Customers: Order Value Distribution
def get_order_value_distribution(start_date=None, end_date=None, state='ALL'):
    where_clause, params = build_where_clause(start_date, end_date, state)
    query = f"""
    SELECT p.payment_value
    FROM dw.fact_payments p
    JOIN dw.fact_orders o ON p.order_id = o.order_id
    JOIN dw.dim_customer c ON o.customer_id = c.customer_id
    WHERE o.order_status = 'delivered' {where_clause}
    """
    return fetch_data(query, params)

# Products & Reviews: Bottom 10 Categories by Avg Review Score
def get_bottom_categories_by_review(start_date=None, end_date=None, state='ALL'):
    where_clause, params = build_where_clause(start_date, end_date, state)
    query = f"""
    SELECT pr.product_category_name_english, ROUND(AVG(r.review_score), 2) as avg_score, COUNT(*) as review_count
    FROM dw.fact_reviews r
    JOIN dw.fact_orders o ON r.order_id = o.order_id
    JOIN dw.fact_order_items oi ON o.order_id = oi.order_id
    JOIN dw.dim_product pr ON oi.product_id = pr.product_id
    JOIN dw.dim_customer c ON o.customer_id = c.customer_id
    WHERE pr.product_category_name_english IS NOT NULL {where_clause}
    GROUP BY pr.product_category_name_english
    HAVING COUNT(*) >= 10
    ORDER BY avg_score ASC
    LIMIT 10;
    """
    return fetch_data(query, params)

# Products & Reviews: Delivery Time vs Review Score
def get_delivery_vs_review(start_date=None, end_date=None, state='ALL'):
    where_clause, params = build_where_clause(start_date, end_date, state)
    query = f"""
    SELECT
        EXTRACT(EPOCH FROM (o.order_delivered_customer_date - o.order_purchase_timestamp))/86400 as delivery_days,
        r.review_score
    FROM dw.fact_reviews r
    JOIN dw.fact_orders o ON r.order_id = o.order_id
    JOIN dw.dim_customer c ON o.customer_id = c.customer_id
    WHERE o.order_status = 'delivered'
      AND o.order_delivered_customer_date IS NOT NULL
      {where_clause}
    """
    return fetch_data(query, params)

# 5. ML Queries
def get_customer_segments():
    query = """
    SELECT segment_name, COUNT(DISTINCT customer_unique_id) as customer_count,
           AVG(recency) as avg_recency, AVG(frequency) as avg_frequency, AVG(monetary) as avg_monetary
    FROM dw.dim_customer_segment
    GROUP BY segment_name
    ORDER BY customer_count DESC;
    """
    return fetch_data(query)

def get_segment_scatter():
    query = """
    SELECT recency, frequency, monetary, segment_name
    FROM dw.dim_customer_segment
    """
    return fetch_data(query)