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

def get_customer_count_by_state():
    query = """
    SELECT customer_state, COUNT(*) as customer_count
    FROM dw.dim_customer
    GROUP BY customer_state
    ORDER BY customer_count DESC;
    """
    try:
        conn = get_db_connection()
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        logger.error(f"Failed to fetch customer data: {e}")
        return pd.DataFrame()
