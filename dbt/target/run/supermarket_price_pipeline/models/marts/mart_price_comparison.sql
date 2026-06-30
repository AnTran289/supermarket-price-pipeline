
  create view "postgres"."gold"."mart_price_comparison__dbt_tmp"
    
    
  as (
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
FROM "postgres"."silver"."stg_supermarket_prices"
WHERE current_price IS NOT NULL
  );