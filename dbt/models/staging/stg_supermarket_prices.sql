-- Grain: one row per combined_product_id.
SELECT
    combined_product_id,
    retailer_product_id,
    product_name,
    brand,
    pack_size,
    current_price,
    unit_price,
    unit_quantity,
    unit_type,
    is_on_promotion,
    save_amount,
    was_price,
    supermarket,
    (current_price IS NULL) AS has_missing_current_price,
    (unit_price IS NULL) AS has_missing_unit_price,
    (was_price < current_price) AS has_invalid_promotion_price
FROM {{ source('silver', 'supermarket_prices') }}
