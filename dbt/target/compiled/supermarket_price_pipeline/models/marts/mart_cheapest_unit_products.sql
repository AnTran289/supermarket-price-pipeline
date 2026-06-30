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
FROM "postgres"."silver"."stg_supermarket_prices"
WHERE unit_price IS NOT NULL
ORDER BY unit_price ASC