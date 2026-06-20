import subprocess
import sys


def run_step(command):
    print(f"\nRunning: {' '.join(command)}")
    subprocess.run(command, check=True)


def main():
    run_step([sys.executable, "src/validate_csv.py"])
    run_step([sys.executable, "src/load_csv_to_postgres.py"])

    print("\nPipeline completed successfully.")


if __name__ == "__main__":
    main()