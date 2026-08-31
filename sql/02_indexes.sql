CREATE INDEX IF NOT EXISTS idx_fact_orders_date ON dw.fact_orders(date_key);
CREATE INDEX IF NOT EXISTS idx_fact_orders_customer ON dw.fact_orders(customer_key);
CREATE INDEX IF NOT EXISTS idx_fact_orders_product ON dw.fact_orders(product_key);
CREATE INDEX IF NOT EXISTS idx_fact_orders_status ON dw.fact_orders(order_status);
CREATE INDEX IF NOT EXISTS idx_customer_country ON dw.dim_customer(country);
CREATE INDEX IF NOT EXISTS idx_product_category ON dw.dim_product(category);
