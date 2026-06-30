import subprocess
import sys


def run_step(command):
    print(f"\nRunning: {' '.join(command)}")
    subprocess.run(command, check=True)


def main():
    run_step([sys.executable, "src/validate_csv.py"])
    run_step([sys.executable, "src/load_csv_to_postgres.py"])

    run_step([
        "dbt",
        "run",
        "--project-dir",
        "dbt"
    ])

    run_step([
        "dbt",
        "test",
        "--project-dir",
        "dbt"
    ])

    print("\nPipeline completed successfully.")


if __name__ == "__main__":
    main()