import os
import psycopg2
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "postgres"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        dbname=os.getenv("POSTGRES_DB", "ecommerce"),
        user=os.getenv("POSTGRES_USER", "ecommerce"),
        password=os.getenv("POSTGRES_PASSWORD", "ecommerce")
    )

def fetch_customer_rfm(conn):
    query = """
    WITH customer_orders AS (
        SELECT 
            c.customer_unique_id,
            o.order_id,
            o.order_purchase_timestamp,
            p.payment_value
        FROM dw.dim_customer c
        JOIN dw.fact_orders o ON c.customer_id = o.customer_id
        JOIN dw.fact_payments p ON o.order_id = p.order_id
        WHERE o.order_status = 'delivered'
    )
    SELECT 
        customer_unique_id,
        MAX(order_purchase_timestamp) as last_purchase_date,
        COUNT(DISTINCT order_id) as frequency,
        SUM(payment_value) as monetary
    FROM customer_orders
    GROUP BY customer_unique_id;
    """
    return pd.read_sql_query(query, conn)

def assign_segment_names(df):
    # Sort clusters by monetary value to assign meaningful names
    cluster_means = df.groupby('cluster_id')['monetary'].mean().sort_values()
    
    # 0 -> Low Value, 1 -> Mid Value, 2 -> High Value, etc. (assuming 4 clusters)
    # Let's map dynamically based on mean monetary
    mapping = {}
    names = ['Churned/Low Value', 'At Risk', 'Promising', 'Champions/Loyal']
    
    for i, (cluster_id, _) in enumerate(cluster_means.items()):
        mapping[cluster_id] = names[min(i, len(names)-1)]
        
    df['segment_name'] = df['cluster_id'].map(mapping)
    return df

def run_segmentation():
    try:
        conn = get_db_connection()
        logger.info("Connected to Data Warehouse.")
        
        # 1. Extract RFM base data
        logger.info("Fetching customer order history...")
        df = fetch_customer_rfm(conn)
        
        if df.empty:
            logger.warning("No data found for segmentation.")
            return

        # 2. Calculate Recency
        # Get the max date in the dataset to act as 'today'
        current_date = df['last_purchase_date'].max()
        df['recency'] = (current_date - df['last_purchase_date']).dt.days

        # 3. Prepare data for KMeans
        features = ['recency', 'frequency', 'monetary']
        X = df[features].copy()
        
        # Fill NA just in case
        X = X.fillna(0)
        
        # Standardize features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # 4. Train KMeans Model
        n_clusters = 4
        logger.info(f"Training K-Means with {n_clusters} clusters...")
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        df['cluster_id'] = kmeans.fit_predict(X_scaled)
        
        # 5. Assign Segment Names
        df = assign_segment_names(df)
        
        # 6. Load back to Data Warehouse
        logger.info("Writing segments back to dw.dim_customer_segment...")
        cursor = conn.cursor()
        
        # Clear existing
        cursor.execute("TRUNCATE TABLE dw.dim_customer_segment;")
        
        # Insert new
        insert_query = """
        INSERT INTO dw.dim_customer_segment (
            customer_unique_id, recency, frequency, monetary, cluster_id, segment_name
        ) VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        # Batch insert
        data_tuples = list(df[['customer_unique_id', 'recency', 'frequency', 'monetary', 'cluster_id', 'segment_name']].itertuples(index=False, name=None))
        
        # For simplicity and speed in python, use execute_batch
        from psycopg2.extras import execute_batch
        execute_batch(cursor, insert_query, data_tuples)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"Successfully segmented {len(df)} customers.")
        
    except Exception as e:
        logger.error(f"Error in segmentation pipeline: {e}")

if __name__ == "__main__":
    run_segmentation()
