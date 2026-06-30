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
FROM "postgres"."silver"."stg_supermarket_prices"
GROUP BY supermarket