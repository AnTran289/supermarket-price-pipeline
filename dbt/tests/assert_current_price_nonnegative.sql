-- A priced listing must not have a negative selling price.
SELECT combined_product_id, current_price
FROM {{ ref('stg_supermarket_prices') }}
WHERE current_price < 0
