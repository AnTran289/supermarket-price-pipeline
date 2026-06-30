
  create view "postgres"."gold"."mart_data_quality_summary__dbt_tmp"
    
    
  as (
    SELECT
    supermarket,
    COUNT(*) AS total_rows,
    COUNT(*) FILTER (
        WHERE product_name IS NULL OR product_name = ''
    ) AS missing_product_name,
    COUNT(*) FILTER (
        WHERE current_price IS NULL
    ) AS missing_current_price,
    COUNT(*) FILTER (
        WHERE unit_price IS NULL
    ) AS missing_unit_price,
    COUNT(*) FILTER (
        WHERE unit_type IS NULL OR unit_type = ''
    ) AS missing_unit_type,
    COUNT(*) FILTER (
        WHERE was_price < current_price
    ) AS invalid_promotion_price
FROM "postgres"."silver"."stg_supermarket_prices"
GROUP BY supermarket
  );