-- 1. Creation of the reconciled layer table
CREATE TABLE IF NOT EXISTS reconciled.movies (
    movie_id SERIAL PRIMARY KEY,
    imdb_id VARCHAR(20),
    tmdb_id INT,
    title VARCHAR(255),
    release_year INT,
    budget NUMERIC,
    revenue NUMERIC,
    runtime INT,
    imdb_rating NUMERIC(3,1),
    imdb_votes INT,
    tmdb_rating NUMERIC(3,1),
    tmdb_votes INT
);

-- 2. Cleaning and reconciliation of data from Kaggle and IMDb
-- Empty the reconciled.movies table before inserting new data
TRUNCATE TABLE reconciled.movies;

INSERT INTO reconciled.movies (
    imdb_id, tmdb_id, title, release_year, budget, revenue, runtime, 
    imdb_rating, imdb_votes, tmdb_rating, tmdb_votes
)
SELECT 
    -- Formatting and cleaning of IDs
    i.tconst AS imdb_id,
    CAST(l.tmdbid AS INT) AS tmdb_id,
    
    -- Cleaning: take the original title from Kaggle, if missing use the IMDb one
    COALESCE(k.original_title, i.primarytitle) AS title,
    
    -- Cleaning: resolve inconsistencies in release year
    CAST(NULLIF(i.startyear, '\N') AS INT) AS release_year,
    
    -- Cleaning budget and revenue (Kaggle)
    CAST(k.budget AS NUMERIC) AS budget,
    CAST(k.revenue AS NUMERIC) AS revenue,
    
    -- Cleaning runtime
    CAST(NULLIF(i.runtimeminutes, '\N') AS INT) AS runtime,
    
    -- IMDB ratings and votes (IMDb)
    CAST(r.averagerating AS NUMERIC(3,1)) AS imdb_rating,
    CAST(r.numvotes AS INT) AS imdb_votes,
    
    -- TMDB ratings and votes (Kaggle)
    CAST(k.vote_average AS NUMERIC(3,1)) AS tmdb_rating,
    CAST(k.vote_count AS INT) AS tmdb_votes

FROM staging.kaggle_movies_metadata k
-- Joining with Kaggle links to map TMDB IDs to IMDb IDs
JOIN staging.kaggle_links l ON k.id = CAST(l.tmdbid AS VARCHAR)
-- Exact match with IMDb title basics to get additional information
JOIN staging.imdb_title_basics i ON l.imdbid = i.tconst
LEFT JOIN staging.imdb_title_ratings r ON i.tconst = r.tconst

-- Deduplication and filtering: only include released movies
WHERE k.status = 'Released' 
  AND i.titletype = 'movie';