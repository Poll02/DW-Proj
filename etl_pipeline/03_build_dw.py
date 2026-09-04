import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

# Create PostgreSQL connection
engine = create_engine(f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}')

def execute_sql_file(file_path):
    print(f"Executing SQL script: {file_path}...")
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            sql_queries = file.read()
            
        with engine.begin() as connection:
            connection.execute(text(sql_queries))
            
        print(f"Successfully executed: {file_path}\n")
    except Exception as e:
        print(f"Error executing {file_path}: {e}\n")
        raise e

if __name__ == "__main__":
    # SQL script paths
    schema_script = 'database/ddl/03_create_dw_schema.sql'
    population_script = 'database/ddl/04_populate_dw.sql'
    
    # 1. Create Data Warehouse schema (Dimensions, Facts, Bridge)
    if os.path.exists(schema_script):
        execute_sql_file(schema_script)
    else:
        print(f"File not found: {schema_script}")

    # 2. Populate Data Warehouse tables from reconciled layer
    if os.path.exists(population_script):
        execute_sql_file(population_script)
    else:
        print(f"File not found: {population_script}")