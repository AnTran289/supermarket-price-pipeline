from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()

CSV_PATH = Path("data/silver/supermarket_prices_silver.csv")

SQL_FILES = [
    "sql/01_create_schemas.sql",
    "sql/02_create_silver_table.sql",
    "sql/03_create_gold_views.sql",
]

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

engine = create_engine(
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)


def run_sql_file(path):
    sql_text = Path(path).read_text(encoding="utf-8")
    statements = [statement.strip() for statement in sql_text.split(";") if statement.strip()]

    with engine.begin() as conn:
        for statement in statements:
            conn.execute(text(statement))


def main():
    print("Creating schemas...")
    run_sql_file("sql/01_create_schemas.sql")

    print("Creating silver table...")
    run_sql_file("sql/02_create_silver_table.sql")

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

    print("Creating Gold views...")
    run_sql_file("sql/03_create_gold_views.sql")

    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM silver.supermarket_prices;"))
        row_count = result.scalar()

    print(f"Pipeline finished successfully. Loaded {row_count} rows.")


if __name__ == "__main__":
    main()
