"""Validate CSV, refresh PostgreSQL Silver, then build and test dbt models."""
import os
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]


def run_step(command: list[str], env: dict[str, str]) -> None:
    print(f"Running: {' '.join(command)}", flush=True)
    subprocess.run(command, check=True, cwd=ROOT, env=env)


def main() -> None:
    load_dotenv(ROOT / ".env")
    env = os.environ.copy()
    run_step([sys.executable, "src/validate_csv.py"], env)
    run_step([sys.executable, "src/load_csv_to_postgres.py"], env)
    run_step(["dbt", "build", "--project-dir", "dbt", "--profiles-dir", "dbt"], env)
    print("Pipeline completed successfully.")


if __name__ == "__main__":
    main()
