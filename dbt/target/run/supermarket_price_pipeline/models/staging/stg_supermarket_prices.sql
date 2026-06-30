
  create view "postgres"."silver"."stg_supermarket_prices__dbt_tmp"
    
    
  as (
    --cleaned staging model
--prepares, standardises, and flags data before Gold models use it
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

    CASE
        WHEN current_price IS NULL THEN TRUE
        ELSE FALSE
    END AS has_missing_current_price,

    CASE
        WHEN unit_price IS NULL THEN TRUE
        ELSE FALSE
    END AS has_missing_unit_price,

    CASE
        WHEN was_price < current_price THEN TRUE
        ELSE FALSE
    END AS has_invalid_promotion_price

FROM "postgres"."silver"."supermarket_prices"
  );