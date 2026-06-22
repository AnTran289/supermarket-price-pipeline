DROP TABLE IF EXISTS silver.supermarket_prices CASCADE;

CREATE TABLE silver.supermarket_prices (
    combined_product_id TEXT PRIMARY KEY,
    retailer_product_id TEXT,
    product_name TEXT NOT NULL,
    brand TEXT,
    pack_size TEXT,
    current_price NUMERIC(10, 2) NOT NULL,
    unit_price NUMERIC(10, 2),
    unit_quantity NUMERIC(10, 2),
    unit_type TEXT,
    is_on_promotion BOOLEAN,
    save_amount NUMERIC(10, 2),
    was_price NUMERIC(10, 2),
    supermarket TEXT NOT NULL
);
