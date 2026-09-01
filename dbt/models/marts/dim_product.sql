{{ config(materialized='table') }}

SELECT
    product_id,
    product_category_name AS product_category_name_english,
    CAST(product_weight_g AS NUMERIC) AS product_weight_g,
    CAST(product_length_cm AS NUMERIC) AS product_length_cm,
    CAST(product_height_cm AS NUMERIC) AS product_height_cm,
    CAST(product_width_cm AS NUMERIC) AS product_width_cm
FROM {{ source('raw', 'products') }}
WHERE product_id IS NOT NULL
