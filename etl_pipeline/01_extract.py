import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

# 1. Creating the connection to PostgreSQL using environment variables
load_dotenv()
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

# 2. Connecting to the PostgreSQL database using SQLAlchemy
engine = create_engine(f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}')

def load_file_to_staging(file_path, table_name, separator=','):
    print(f"Starting to load {file_path} into staging.{table_name}...")
    try:
        # Chunksize divide the file into smaller parts to avoid memory issues
        chunk_size = 100000
        for chunk in pd.read_csv(file_path, sep=separator, chunksize=chunk_size, low_memory=False):
            # if_exists='append' ensures that if the table already exists, new data will be appended to it
            chunk.to_sql(name=table_name, schema='staging', con=engine, if_exists='append', index=False)
        print(f"Completed loading {table_name}!\n")
    except Exception as e:
        print(f"Error occurred while loading {table_name}: {e}\n")

if __name__ == "__main__":
    # KAGGLE Datasets 
    load_file_to_staging('datasets/source_kaggle/links.csv', 'kaggle_links', separator=',')
    
    load_file_to_staging('datasets/source_kaggle/movies_metadata.csv', 'kaggle_movies_metadata', separator=',')
    load_file_to_staging('datasets/source_kaggle/credits.csv', 'kaggle_credits', separator=',')
    load_file_to_staging('datasets/source_kaggle/keywords.csv', 'kaggle_keywords', separator=',')

    # IMDB DATASETS 
    load_file_to_staging('datasets/source_imdb/title.basics.tsv', 'imdb_title_basics', separator='\t')
    load_file_to_staging('datasets/source_imdb/title.ratings.tsv', 'imdb_title_ratings', separator='\t')
    load_file_to_staging('datasets/source_imdb/title.crew.tsv', 'imdb_title_crew', separator='\t')
    load_file_to_staging('datasets/source_imdb/name.basics.tsv', 'imdb_name_basics', separator='\t')