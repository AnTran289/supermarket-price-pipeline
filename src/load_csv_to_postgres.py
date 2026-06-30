from pathlib import Path
import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

# --------------------------------------------------
# Project paths
# --------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]

CSV_PATH = PROJECT_ROOT / "data" / "silver" / "supermarket_prices_silver.csv"

CREATE_SCHEMAS_SQL = PROJECT_ROOT / "sql" / "01_create_schemas.sql"
CREATE_SILVER_TABLE_SQL = PROJECT_ROOT / "sql" / "02_create_silver_table.sql"

# --------------------------------------------------
# Load environment variables
# --------------------------------------------------
load_dotenv(PROJECT_ROOT / ".env")

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

required_env_vars = {
    "DB_USER": DB_USER,
    "DB_PASSWORD": DB_PASSWORD,
    "DB_HOST": DB_HOST,
    "DB_PORT": DB_PORT,
    "DB_NAME": DB_NAME,
}

missing_vars = [key for key, value in required_env_vars.items() if not value]

if missing_vars:
    raise ValueError(
        f"Missing environment variables: {missing_vars}. "
        "Check that .env exists in the project root and has one variable per line."
    )

DATABASE_URL = URL.create(
    drivername="postgresql+psycopg2",
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=int(DB_PORT),
    database=DB_NAME,
)

engine = create_engine(DATABASE_URL)


# --------------------------------------------------
# Helper function
# --------------------------------------------------
def run_sql_file(path: Path):
    sql_text = path.read_text(encoding="utf-8")
    statements = [
        statement.strip()
        for statement in sql_text.split(";")
        if statement.strip()
    ]

    with engine.begin() as conn:
        for statement in statements:
            conn.execute(text(statement))


# --------------------------------------------------
# Main pipeline step
# --------------------------------------------------
def main():
    print("Creating schemas...")
    run_sql_file(CREATE_SCHEMAS_SQL)

    print("Creating silver table...")
    run_sql_file(CREATE_SILVER_TABLE_SQL)

    print("Reading CSV...")
    df = pd.read_csv(CSV_PATH)

    expected_order = [
        "combined_product_id",
        "retailer_product_id",
        "product_name",
        "brand",
        "pack_size",
        "current_price",
        "unit_price",
        "unit_quantity",
        "unit_type",
        "is_on_promotion",
        "save_amount",
        "was_price",
        "supermarket",
    ]

    missing_columns = [col for col in expected_order if col not in df.columns]

    if missing_columns:
        raise ValueError(f"Missing columns in CSV: {missing_columns}")

    df = df[expected_order]

    print("Loading CSV into PostgreSQL...")
    df.to_sql(
        name="supermarket_prices",
        con=engine,
        schema="silver",
        if_exists="append",
        index=False,
        method="multi",
        chunksize=1000,
    )

    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT COUNT(*) FROM silver.supermarket_prices;")
        )
        row_count = result.scalar()

    print(f"Pipeline finished successfully. Loaded {row_count} rows.")


if __name__ == "__main__":
    main()