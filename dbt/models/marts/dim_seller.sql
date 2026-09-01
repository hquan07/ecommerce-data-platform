{{ config(materialized='table') }}

SELECT
    seller_id,
    seller_zip_code_prefix,
    seller_city,
    seller_state
FROM {{ source('raw', 'sellers') }}
WHERE seller_id IS NOT NULL
