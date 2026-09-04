-- 1. Dimension Tables
CREATE TABLE IF NOT EXISTS dw.dim_time (
    time_key SERIAL PRIMARY KEY,
    release_year INT UNIQUE,
    decade VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS dw.dim_geography (
    geo_key SERIAL PRIMARY KEY,
    country_code VARCHAR(10),
    country_name VARCHAR(100),
    continent VARCHAR(50),
    UNIQUE (country_code, country_name, continent)
);

CREATE TABLE IF NOT EXISTS dw.dim_director (
    director_key SERIAL PRIMARY KEY,
    director_id VARCHAR(20) UNIQUE,
    director_name VARCHAR(255),
    birth_year INT,
    death_year INT
);

-- Snowflake hierarchy: Macro-genre -> Genre
CREATE TABLE IF NOT EXISTS dw.dim_macro_genre (
    macro_genre_key SERIAL PRIMARY KEY,
    macro_genre_name VARCHAR(100) UNIQUE
);

CREATE TABLE IF NOT EXISTS dw.dim_genre (
    genre_key SERIAL PRIMARY KEY,
    genre_name VARCHAR(100) UNIQUE,
    macro_genre_key INT REFERENCES dw.dim_macro_genre(macro_genre_key)
);

-- 2. Fact Table: Fact_Movie_Performance
CREATE TABLE IF NOT EXISTS dw.fact_movie_performance (
    fact_key SERIAL PRIMARY KEY,
    movie_id INT,
    imdb_id VARCHAR(20),
    title VARCHAR(500),
    time_key INT REFERENCES dw.dim_time(time_key),
    geo_key INT REFERENCES dw.dim_geography(geo_key),
    director_key INT REFERENCES dw.dim_director(director_key),
    budget NUMERIC,
    revenue NUMERIC,
    profit NUMERIC,
    runtime INT,
    imdb_rating NUMERIC(3,1),
    imdb_votes INT,
    tmdb_rating NUMERIC(3,1),
    tmdb_votes INT
);

-- 3. Bridge Table for Multivalued Genres
CREATE TABLE IF NOT EXISTS dw.bridge_movie_genre (
    fact_key INT REFERENCES dw.fact_movie_performance(fact_key),
    genre_key INT REFERENCES dw.dim_genre(genre_key),
    PRIMARY KEY (fact_key, genre_key)
);