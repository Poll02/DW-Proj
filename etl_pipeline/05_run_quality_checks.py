import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

engine = create_engine(f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}')

def run_quality_checks():
    sql_file = 'database/ddl/05_quality_checks.sql'
    print("Running Data Quality Checks on Data Warehouse...")
    
    if not os.path.exists(sql_file):
        print(f"File not found: {sql_file}")
        return

    with open(sql_file, 'r', encoding='utf-8') as f:
        queries = f.read()

    # Split script into individual SELECT blocks
    individual_queries = [q.strip() for q in queries.split(';') if q.strip()]
    
    all_passed = True
    for query in individual_queries:
        df = pd.read_sql(text(query), engine)
        for _, row in df.iterrows():
            check_name = row['check_name']
            failed = row['failed_records']
            if failed == 0:
                print(f"[PASS] {check_name}: 0 failures")
            else:
                print(f"[FAIL] {check_name}: {failed} failures detected")
                all_passed = False

    print("-" * 50)
    if all_passed:
        print("All Quality Checks passed successfully.")
    else:
        print("Some Quality Checks reported inconsistencies.")

if __name__ == "__main__":
    run_quality_checks()