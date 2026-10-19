"""Load the validated full CSV snapshot into PostgreSQL transactionally."""
from pathlib import Path
import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data/silver/supermarket_prices_silver.csv"
load_dotenv(ROOT / ".env")

required = ["DB_USER", "DB_PASSWORD", "DB_HOST", "DB_PORT", "DB_NAME"]
missing = [key for key in required if not os.getenv(key)]
if missing:
    raise ValueError(f"Missing database environment variables: {missing}")

engine = create_engine(URL.create(
    "postgresql+psycopg2",
    username=os.environ["DB_USER"],
    password=os.environ["DB_PASSWORD"],
    host=os.environ["DB_HOST"],
    port=int(os.environ["DB_PORT"]),
    database=os.environ["DB_NAME"],
))

COLUMNS = [
    "combined_product_id", "retailer_product_id", "product_name", "brand",
    "pack_size", "current_price", "unit_price", "unit_quantity", "unit_type",
    "is_on_promotion", "save_amount", "was_price", "supermarket",
]


def run_sql_file(path: Path) -> None:
    # Driver handles semicolons in comments/strings; do not split SQL manually.
    with engine.begin() as conn:
        conn.exec_driver_sql(path.read_text(encoding="utf-8"))


def main() -> None:
    df = pd.read_csv(CSV_PATH)
    missing_columns = sorted(set(COLUMNS) - set(df.columns))
    if missing_columns:
        raise ValueError(f"Missing CSV columns: {missing_columns}")
    df = df[COLUMNS]

    run_sql_file(ROOT / "sql/01_create_schemas.sql")
    run_sql_file(ROOT / "sql/02_create_silver_table.sql")

    # Full snapshot: delete and insert within the SAME transaction.
    # A failed insert rolls back the delete; table/views remain intact.
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM silver.supermarket_prices"))
        df.to_sql(
            name="supermarket_prices", con=conn, schema="silver",
            if_exists="append", index=False, method="multi", chunksize=1000,
        )
        count = conn.execute(text("SELECT COUNT(*) FROM silver.supermarket_prices")).scalar_one()
    print(f"Pipeline finished successfully. Loaded {count} rows.")


if __name__ == "__main__":
    main()
