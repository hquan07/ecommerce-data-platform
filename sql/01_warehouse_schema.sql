CREATE SCHEMA IF NOT EXISTS dw;

CREATE TABLE IF NOT EXISTS dw.dim_customer (
    customer_id                 VARCHAR(64) PRIMARY KEY,
    customer_unique_id          VARCHAR(64) NOT NULL,
    customer_zip_code_prefix    VARCHAR(20),
    customer_city               VARCHAR(100),
    customer_state              VARCHAR(2)
);

CREATE TABLE IF NOT EXISTS dw.dim_seller (
    seller_id                   VARCHAR(64) PRIMARY KEY,
    seller_zip_code_prefix      VARCHAR(20),
    seller_city                 VARCHAR(100),
    seller_state                VARCHAR(2)
);

CREATE TABLE IF NOT EXISTS dw.dim_product (
    product_id                      VARCHAR(64) PRIMARY KEY,
    product_category_name_english   VARCHAR(100),
    product_weight_g                NUMERIC,
    product_length_cm               NUMERIC,
    product_height_cm               NUMERIC,
    product_width_cm                NUMERIC
);

CREATE TABLE IF NOT EXISTS dw.fact_orders (
    order_id                        VARCHAR(64) PRIMARY KEY,
    customer_id                     VARCHAR(64) NOT NULL REFERENCES dw.dim_customer(customer_id),
    order_status                    VARCHAR(30),
    order_purchase_timestamp        TIMESTAMP,
    order_approved_at               TIMESTAMP,
    order_delivered_carrier_date    TIMESTAMP,
    order_delivered_customer_date   TIMESTAMP,
    order_estimated_delivery_date   TIMESTAMP
);

CREATE TABLE IF NOT EXISTS dw.fact_order_items (
    order_id                VARCHAR(64) NOT NULL REFERENCES dw.fact_orders(order_id),
    order_item_id           INTEGER NOT NULL,
    product_id              VARCHAR(64) NOT NULL REFERENCES dw.dim_product(product_id),
    seller_id               VARCHAR(64) NOT NULL REFERENCES dw.dim_seller(seller_id),
    shipping_limit_date     TIMESTAMP,
    price                   NUMERIC(12,2) NOT NULL,
    freight_value           NUMERIC(12,2) NOT NULL,
    PRIMARY KEY (order_id, order_item_id)
);

CREATE TABLE IF NOT EXISTS dw.fact_payments (
    order_id                VARCHAR(64) NOT NULL REFERENCES dw.fact_orders(order_id),
    payment_sequential      INTEGER NOT NULL,
    payment_type            VARCHAR(50),
    payment_installments    INTEGER,
    payment_value           NUMERIC(12,2),
    PRIMARY KEY (order_id, payment_sequential)
);

CREATE TABLE IF NOT EXISTS dw.realtime_sales_metrics (
    window_start            TIMESTAMP NOT NULL,
    window_end              TIMESTAMP NOT NULL,
    total_orders            INTEGER NOT NULL,
    total_revenue           NUMERIC(14,2) NOT NULL,
    unique_customers        INTEGER NOT NULL,
    PRIMARY KEY (window_start, window_end)
);
