CREATE OR REPLACE VIEW gold.price_comparison AS
SELECT
    combined_product_id,
    supermarket,
    product_name,
    brand,
    pack_size,
    current_price,
    unit_price,
    unit_quantity,
    unit_type,
    is_on_promotion,
    save_amount,
    was_price
FROM silver.supermarket_prices
WHERE current_price IS NOT NULL;

CREATE OR REPLACE VIEW gold.promotion_summary AS
SELECT
    supermarket,
    COUNT(*) AS total_products,
    COUNT(*) FILTER (WHERE is_on_promotion = TRUE) AS products_on_promotion,
    ROUND(
        COUNT(*) FILTER (WHERE is_on_promotion = TRUE)::NUMERIC
        / COUNT(*) * 100,
        2
    ) AS promotion_percentage,
    ROUND(AVG(save_amount), 2) AS avg_save_amount
FROM silver.supermarket_prices
GROUP BY supermarket
ORDER BY promotion_percentage DESC;

CREATE OR REPLACE VIEW gold.cheapest_unit_products AS
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
FROM silver.supermarket_prices
WHERE unit_price IS NOT NULL
ORDER BY unit_price ASC;

CREATE OR REPLACE VIEW gold.data_quality_summary AS
SELECT
    supermarket,
    COUNT(*) AS total_rows,
    COUNT(*) FILTER (WHERE product_name IS NULL OR product_name = '') AS missing_product_name,
    COUNT(*) FILTER (WHERE current_price IS NULL) AS missing_current_price,
    COUNT(*) FILTER (WHERE unit_price IS NULL) AS missing_unit_price,
    COUNT(*) FILTER (WHERE unit_type IS NULL OR unit_type = '') AS missing_unit_type,
    COUNT(*) FILTER (WHERE was_price < current_price) AS invalid_promotion_price
FROM silver.supermarket_prices
GROUP BY supermarket
ORDER BY supermarket;
