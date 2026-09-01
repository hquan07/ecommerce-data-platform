CREATE TABLE IF NOT EXISTS dw.dim_customer_segment (
    customer_unique_id VARCHAR(64) PRIMARY KEY,
    recency NUMERIC(10, 2),
    frequency INTEGER,
    monetary NUMERIC(14, 2),
    cluster_id INTEGER,
    segment_name VARCHAR(50),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
