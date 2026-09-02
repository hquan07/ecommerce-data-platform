{{ config(
    materialized='table',
    indexes=[
      {'columns': ['order_id']}
    ]
) }}

SELECT
    review_id,
    order_id,
    CAST(review_score AS INTEGER) AS review_score,
    review_comment_title,
    review_comment_message,
    CAST(review_creation_date AS TIMESTAMP) AS review_creation_date,
    CAST(review_answer_timestamp AS TIMESTAMP) AS review_answer_timestamp
FROM {{ source('raw', 'order_reviews') }}
WHERE review_score IS NOT NULL
