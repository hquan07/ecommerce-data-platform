CREATE SCHEMA IF NOT EXISTS dw;

CREATE TABLE IF NOT EXISTS dw.dim_date (
    date_key        INTEGER PRIMARY KEY,
    full_date       DATE NOT NULL UNIQUE,
    year            INTEGER NOT NULL,
    quarter         INTEGER NOT NULL,
    month           INTEGER NOT NULL,
    month_name      VARCHAR(20) NOT NULL,
    week_of_year    INTEGER NOT NULL,
    day_of_month    INTEGER NOT NULL,
    day_of_week     INTEGER NOT NULL,
    day_name        VARCHAR(20) NOT NULL
);

CREATE TABLE IF NOT EXISTS dw.dim_customer (
    customer_key    BIGSERIAL PRIMARY KEY,
    customer_id     VARCHAR(64) NOT NULL UNIQUE,
    full_name       VARCHAR(255),
    email           VARCHAR(255),
    city            VARCHAR(100),
    country         VARCHAR(100),
    segment         VARCHAR(50),
    effective_from  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    effective_to    TIMESTAMP,
    is_current      BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS dw.dim_product (
    product_key     BIGSERIAL PRIMARY KEY,
    product_id      VARCHAR(64) NOT NULL UNIQUE,
    product_name    VARCHAR(255) NOT NULL,
    category        VARCHAR(100),
    subcategory     VARCHAR(100),
    brand           VARCHAR(100),
    unit_price      NUMERIC(12,2)
);

CREATE TABLE IF NOT EXISTS dw.dim_store (
    store_key       BIGSERIAL PRIMARY KEY,
    store_id        VARCHAR(64) NOT NULL UNIQUE,
    store_name      VARCHAR(255),
    city            VARCHAR(100),
    country         VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS dw.fact_orders (
    order_key       BIGSERIAL PRIMARY KEY,
    order_id        VARCHAR(64) NOT NULL UNIQUE,
    date_key        INTEGER NOT NULL REFERENCES dw.dim_date(date_key),
    customer_key    BIGINT NOT NULL REFERENCES dw.dim_customer(customer_key),
    product_key     BIGINT NOT NULL REFERENCES dw.dim_product(product_key),
    store_key       BIGINT REFERENCES dw.dim_store(store_key),
    quantity        INTEGER NOT NULL CHECK (quantity > 0),
    unit_price      NUMERIC(12,2) NOT NULL CHECK (unit_price >= 0),
    discount_amount NUMERIC(12,2) NOT NULL DEFAULT 0 CHECK (discount_amount >= 0),
    gross_amount    NUMERIC(14,2) NOT NULL,
    net_amount      NUMERIC(14,2) NOT NULL,
    payment_method  VARCHAR(50),
    order_status    VARCHAR(30),
    created_at      TIMESTAMP NOT NULL
);
