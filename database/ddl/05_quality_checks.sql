-- Quality Check 1: Check for orphan records in Fact Table (Foreign Key Integrity)
SELECT 'Orphan time keys' AS check_name, COUNT(*) AS failed_records
FROM dw.fact_movie_performance f
LEFT JOIN dw.dim_time t ON f.time_key = t.time_key
WHERE f.time_key IS NOT NULL AND t.time_key IS NULL

UNION ALL

SELECT 'Orphan geography keys', COUNT(*)
FROM dw.fact_movie_performance f
LEFT JOIN dw.dim_geography g ON f.geo_key = g.geo_key
WHERE f.geo_key IS NOT NULL AND g.geo_key IS NULL

UNION ALL

SELECT 'Orphan director keys', COUNT(*)
FROM dw.fact_movie_performance f
LEFT JOIN dw.dim_director d ON f.director_key = d.director_key
WHERE f.director_key IS NOT NULL AND d.director_key IS NULL;


-- Quality Check 2: Check bridge table integrity
SELECT 'Bridge table orphan facts' AS check_name, COUNT(*) AS failed_records
FROM dw.bridge_movie_genre b
LEFT JOIN dw.fact_movie_performance f ON b.fact_key = f.fact_key
WHERE f.fact_key IS NULL

UNION ALL

SELECT 'Bridge table orphan genres', COUNT(*)
FROM dw.bridge_movie_genre b
LEFT JOIN dw.dim_genre g ON b.genre_key = g.genre_key
WHERE g.genre_key IS NULL;


-- Quality Check 3: Check financial logic consistency (Revenue - Budget = Profit)
SELECT 'Financial calculation inconsistencies' AS check_name, COUNT(*) AS failed_records
FROM dw.fact_movie_performance
WHERE budget IS NOT NULL 
  AND revenue IS NOT NULL 
  AND profit <> (revenue - budget);


-- Quality Check 4: Rating range validity (Ratings must be between 1.0 and 10.0 when present)
SELECT 'Invalid IMDb rating range' AS check_name, COUNT(*) AS failed_records
FROM dw.fact_movie_performance
WHERE imdb_rating IS NOT NULL AND (imdb_rating < 1.0 OR imdb_rating > 10.0)

UNION ALL

SELECT 'Invalid TMDB rating range', COUNT(*)
FROM dw.fact_movie_performance
WHERE tmdb_rating IS NOT NULL AND (tmdb_rating < 1.0 OR tmdb_rating > 10.0);