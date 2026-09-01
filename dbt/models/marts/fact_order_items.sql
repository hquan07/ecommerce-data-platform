{{ config(materialized='table') }}

SELECT
    order_id,
    CAST(order_item_id AS INTEGER) AS order_item_id,
    product_id,
    seller_id,
    CAST(shipping_limit_date AS TIMESTAMP) AS shipping_limit_date,
    CAST(price AS NUMERIC(12,2)) AS price,
    CAST(freight_value AS NUMERIC(12,2)) AS freight_value
FROM {{ source('raw', 'order_items') }}
WHERE order_id IS NOT NULL
