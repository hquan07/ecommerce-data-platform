CREATE OR REPLACE VIEW dw.vw_daily_revenue AS
SELECT 
    DATE(order_purchase_timestamp) AS order_date,
    COUNT(DISTINCT o.order_id) AS total_orders,
    SUM(oi.price + oi.freight_value) AS total_revenue
FROM dw.fact_orders o
JOIN dw.fact_order_items oi ON o.order_id = oi.order_id
WHERE o.order_status = 'delivered'
GROUP BY 1
ORDER BY 1;

CREATE OR REPLACE VIEW dw.vw_category_sales AS
SELECT 
    p.product_category_name_english AS category,
    COUNT(oi.product_id) AS items_sold,
    SUM(oi.price) AS total_revenue
FROM dw.fact_order_items oi
JOIN dw.dim_product p ON oi.product_id = p.product_id
JOIN dw.fact_orders o ON oi.order_id = o.order_id
WHERE o.order_status = 'delivered'
GROUP BY 1
ORDER BY 3 DESC;

CREATE OR REPLACE VIEW dw.vw_customer_distribution AS
SELECT 
    customer_state,
    COUNT(DISTINCT customer_unique_id) AS total_customers
FROM dw.dim_customer
GROUP BY 1
ORDER BY 2 DESC;
