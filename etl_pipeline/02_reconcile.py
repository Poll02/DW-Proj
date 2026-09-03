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
            # text() is required in SQLAlchemy 2.0+ to execute raw SQL statements
            connection.execute(text(sql_queries))
            
        print("Execution completed successfully.\n")
    except Exception as e:
        print(f"Error executing {file_path}: {e}\n")

if __name__ == "__main__":
    # Ensure the path points to the SQL file created in the previous step
    sql_file_path = 'database/ddl/02_reconciled_layer.sql'
    
    if os.path.exists(sql_file_path):
        execute_sql_file(sql_file_path)
    else:
        print(f"File not found: {sql_file_path}")