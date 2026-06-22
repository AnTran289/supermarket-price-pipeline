from pathlib import Path
import sys
import pandas as pd

CSV_PATH = Path("data/silver/supermarket_prices_silver.csv")
REPORT_DIR = Path("data/quality_reports")
REPORT_PATH = REPORT_DIR / "validation_report.csv"

REQUIRED_COLUMNS = [
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

VALID_SUPERMARKETS = {"Coles", "Woolworths", "Aldi"}


def main():
    if not CSV_PATH.exists():
        print(f"ERROR: CSV file not found: {CSV_PATH}")
        sys.exit(1)

    df = pd.read_csv(CSV_PATH)

    issues = []

    missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_columns:
        issues.append({
            "severity": "ERROR",
            "check": "missing_columns",
            "details": ", ".join(missing_columns),
        })

    if missing_columns:
        save_report(issues)
        print("Validation failed: missing required columns.")
        sys.exit(1)

    if df["combined_product_id"].isna().any():
        issues.append({
            "severity": "ERROR",
            "check": "combined_product_id_null",
            "details": "combined_product_id contains null values",
        })

    duplicate_ids = df["combined_product_id"].duplicated().sum()
    if duplicate_ids > 0:
        issues.append({
            "severity": "ERROR",
            "check": "duplicate_combined_product_id",
            "details": f"{duplicate_ids} duplicate IDs found",
        })

    if df["product_name"].isna().any():
        issues.append({
            "severity": "ERROR",
            "check": "product_name_null",
            "details": "product_name contains null values",
        })

    if df["current_price"].isna().any():
        issues.append({
            "severity": "ERROR",
            "check": "current_price_null",
            "details": "current_price contains null values",
        })

    invalid_supermarkets = set(df["supermarket"].dropna().unique()) - VALID_SUPERMARKETS
    if invalid_supermarkets:
        issues.append({
            "severity": "ERROR",
            "check": "invalid_supermarket",
            "details": ", ".join(invalid_supermarkets),
        })

    missing_unit_price = df["unit_price"].isna().sum()
    if missing_unit_price > 0:
        issues.append({
            "severity": "WARNING",
            "check": "missing_unit_price",
            "details": f"{missing_unit_price} rows missing unit_price",
        })

    invalid_promo = df[
        df["was_price"].notna()
        & df["current_price"].notna()
        & (df["was_price"] < df["current_price"])
    ]

    if len(invalid_promo) > 0:
        issues.append({
            "severity": "WARNING",
            "check": "was_price_lower_than_current_price",
            "details": f"{len(invalid_promo)} rows have was_price < current_price",
        })

    save_report(issues)

    errors = [issue for issue in issues if issue["severity"] == "ERROR"]

    if errors:
        print("Validation failed.")
        for issue in errors:
            print(f"{issue['check']}: {issue['details']}")
        sys.exit(1)

    print("Validation passed.")
    print(f"Rows checked: {len(df)}")
    print(f"Report saved to: {REPORT_PATH}")


def save_report(issues):
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    if issues:
        pd.DataFrame(issues).to_csv(REPORT_PATH, index=False)
    else:
        pd.DataFrame(
            [{"severity": "INFO", "check": "all_checks_passed", "details": "No critical issues found"}]
        ).to_csv(REPORT_PATH, index=False)


if __name__ == "__main__":
    main()
