-- Populate Dim_Time
INSERT INTO dw.dim_time (release_year, decade)
SELECT DISTINCT 
    release_year,
    CONCAT(CAST((release_year / 10) * 10 AS VARCHAR), 's') AS decade
FROM reconciled.movies
WHERE release_year IS NOT NULL
ON CONFLICT (release_year) DO NOTHING;

-- Populate Dim_Geography
INSERT INTO dw.dim_geography (country_code, country_name, continent)
SELECT DISTINCT country_code, country_name, continent
FROM reconciled.movie_geography
ON CONFLICT (country_code, country_name, continent) DO NOTHING;

-- Populate Dim_Director
INSERT INTO dw.dim_director (director_id, director_name, birth_year, death_year)
SELECT DISTINCT director_id, director_name, birth_year, death_year
FROM reconciled.movie_directors
ON CONFLICT (director_id) DO NOTHING;

-- Populate Macro Genres & Genres
INSERT INTO dw.dim_macro_genre (macro_genre_name)
VALUES 
    ('Narrative & Drama'), 
    ('Action & Adventure'), 
    ('Comedy & Family'), 
    ('Horror & Thriller'), 
    ('Other')
ON CONFLICT (macro_genre_name) DO NOTHING;

INSERT INTO dw.dim_genre (genre_name, macro_genre_key)
SELECT DISTINCT 
    g.genre_name,
    CASE 
        WHEN g.genre_name IN ('Drama', 'Romance', 'Biography', 'History') 
            THEN (SELECT macro_genre_key FROM dw.dim_macro_genre WHERE macro_genre_name = 'Narrative & Drama')
        WHEN g.genre_name IN ('Action', 'Adventure', 'Sci-Fi', 'Western', 'War') 
            THEN (SELECT macro_genre_key FROM dw.dim_macro_genre WHERE macro_genre_name = 'Action & Adventure')
        WHEN g.genre_name IN ('Comedy', 'Family', 'Animation', 'Musical') 
            THEN (SELECT macro_genre_key FROM dw.dim_macro_genre WHERE macro_genre_name = 'Comedy & Family')
        WHEN g.genre_name IN ('Horror', 'Mystery', 'Thriller', 'Crime') 
            THEN (SELECT macro_genre_key FROM dw.dim_macro_genre WHERE macro_genre_name = 'Horror & Thriller')
        ELSE (SELECT macro_genre_key FROM dw.dim_macro_genre WHERE macro_genre_name = 'Other')
    END
FROM reconciled.movie_genres g
ON CONFLICT (genre_name) DO NOTHING;

-- Populate Fact_Movie_Performance
TRUNCATE TABLE dw.bridge_movie_genre, dw.fact_movie_performance CASCADE;

INSERT INTO dw.fact_movie_performance (
    movie_id, imdb_id, title, time_key, geo_key, director_key,
    budget, revenue, profit, runtime, imdb_rating, imdb_votes, tmdb_rating, tmdb_votes
)
SELECT 
    m.movie_id,
    m.imdb_id,
    m.title,
    t.time_key,
    g.geo_key,
    d.director_key,
    m.budget,
    m.revenue,
    (m.revenue - m.budget) AS profit,
    m.runtime,
    m.imdb_rating,
    m.imdb_votes,
    m.tmdb_rating,
    m.tmdb_votes
FROM reconciled.movies m
LEFT JOIN dw.dim_time t ON m.release_year = t.release_year
LEFT JOIN reconciled.movie_geography mg ON m.imdb_id = mg.imdb_id
LEFT JOIN dw.dim_geography g ON mg.country_code = g.country_code AND mg.continent = g.continent
LEFT JOIN reconciled.movie_directors md ON m.imdb_id = md.imdb_id
LEFT JOIN dw.dim_director d ON md.director_id = d.director_id;

-- Populate Bridge Table
INSERT INTO dw.bridge_movie_genre (fact_key, genre_key)
SELECT DISTINCT
    f.fact_key,
    dg.genre_key
FROM dw.fact_movie_performance f
JOIN reconciled.movie_genres rg ON f.imdb_id = rg.imdb_id
JOIN dw.dim_genre dg ON rg.genre_name = dg.genre_name;