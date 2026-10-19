-- This mart is a set of unit-priced listings, not a matched-product winner ranking.
SELECT
    combined_product_id,
    supermarket,
    product_name,
    brand,
    pack_size,
    current_price,
    unit_price,
    unit_quantity,
    unit_type
FROM {{ ref('stg_supermarket_prices') }}
WHERE unit_price IS NOT NULL
