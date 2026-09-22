# Movie Analytics Data Warehouse (DW-Proj)

[![Course](https://img.shields.io/badge/Course-Data%20Management-blue.svg)](https://www.uniroma1.it/)
[![Institution](https://img.shields.io/badge/University-Sapienza%20University%20of%20Rome-red.svg)](https://www.uniroma1.it/)
[![Academic Year](https://img.shields.io/badge/Academic%20Year-2025%2F2026-green.svg)](#)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14%2B-336791?logo=postgresql)](https://www.postgresql.org/)

An end-to-end Data Warehousing and Business Intelligence solution for movie industry analytics. This project integrates multi-gigabyte heterogeneous datasets from **IMDb** and **Kaggle (TMDB)**, cleanses and reconciles them into an operational staging/reconciled layer, models the data into a **Snowflake Schema** based on a **Dimensional Fact Model (DFM)**, and produces OLAP analytical insights alongside automated data quality validation.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Project Objectives](#project-objectives)
- [System Architecture](#system-architecture)
- [Data Sources](#data-sources)
- [Dimensional Modeling](#dimensional-modeling)
- [Repository Structure](#repository-structure)
- [Steps to Reproduce the Pipeline](#steps-to-reproduce-the-pipeline)
  - [1. Prerequisites](#1-prerequisites)
  - [2. Clone and Setup Environment](#2-clone-and-setup-environment)
  - [3. Database Configuration](#3-database-configuration)
  - [4. Schema Initialization](#4-schema-initialization)
  - [5. Dataset Preparation](#5-dataset-preparation)
  - [6. Staging Data Extraction](#6-staging-data-extraction)
  - [7. Run the End-to-End Pipeline](#7-run-the-end-to-end-pipeline)
  - [Alternative: Step-by-Step Execution](#alternative-step-by-step-execution)
- [Analytical Insights & Visualizations](#analytical-insights--visualizations)
- [Automated Data Quality Assurance](#automated-data-quality-assurance)
- [Project Deliverables](#project-deliverables)

---

## Project Overview

In the modern entertainment landscape, making data-driven decisions requires combining data from disparate sources: box-office financial figures, platform user ratings, geographical release contexts, and talent information (directors and crew).

This project designs and implements a complete Data Warehouse lifecycle:
1. **Extraction & Staging**: Ingesting raw, non-reconciled datasets into PostgreSQL in chunks to avoid memory bottlenecks.
2. **Reconciliation & Cleaning**: Standardizing identifiers, regex parsing embedded JSON objects, sanitizing dirty monetary fields, handling missing values, and unnesting multivalued attributes.
3. **Data Warehousing (Snowflake Schema)**: Structuring data into fact, dimension, and bridge tables according to the Dimensional Fact Model.
4. **OLAP Analytics & Visualizations**: Executing analytical SQL queries to examine profitability, ratings divergence, continent distributions, and decade-long historical trends.
5. **Quality Assurance**: Verifying referential integrity, domain constraints, and arithmetic accuracy using automated test suites.

---

## Project Objectives

1. **Heterogeneous Data Integration**:
   - Merge non-commercial official dumps from **IMDb** with metadata from **Kaggle's The Movies Dataset** (sourced from TMDB).
   - Resolve entity identification by joining IMDb ID (`tconst`) with padded TMDB link mappings (`CONCAT('tt', LPAD(imdbId, 7, '0'))`).
2. **Data Cleansing & Transformation**:
   - Parse semi-structured JSON strings in SQL using regular expressions (e.g., ISO country codes and names from production country fields).
   - Sanitize financial attributes (removing non-numeric characters, filtering out negative and zero anomalies).
   - Unnest multi-valued fields into normalized relational forms (comma-separated genre lists and director identifiers).
3. **Dimensional Fact Modeling**:
   - Formulate a formal **Dimensional Fact Model (DFM)** centered around movie performance metrics.
   - Implement a **Snowflake Schema** featuring a macro-genre hierarchy and a bridge table to handle many-to-many movie-genre relationships.
4. **Business Intelligence & OLAP Reporting**:
   - Address key business and academic questions regarding box office trends, profit margins per genre, runtime impact, and rating consistency across platforms.
5. **Data Quality & Pipeline Automation**:
   - Guarantee warehouse reliability through automated integrity checks (orphan keys, mathematical consistency, range validity).
   - Provide a single-command automated orchestrator to execute the pipeline reproducibly.

---

## System Architecture

The warehouse architecture follows a 4-tier data engineering pipeline:

```
+------------------------------------+-----------------------------------+
|            IMDb Dumps              |         Kaggle / TMDB             |
| (title.basics, ratings, crew, name)| (movies_metadata, links, credits) |
+------------------------------------+-----------------------------------+
                                  |
                                  v  [01_extract.py] (Chunked Ingestion)
+------------------------------------------------------------------------+
|                            STAGING LAYER                               |
| Schema: staging                                                        |
| (staging.imdb_*, staging.kaggle_*)                                     |
+------------------------------------------------------------------------+
                                  |
                                  v  [02_reconcile.py / 02_reconciled_layer.sql]
+------------------------------------------------------------------------+
|                          RECONCILED LAYER                              |
| Schema: reconciled                                                     |
| - reconciled.movies           - reconciled.movie_directors             |
| - reconciled.movie_genres     - reconciled.movie_geography             |
+------------------------------------------------------------------------+
                                  |
                                  v  [03_build_dw.py / 03_create_dw_schema.sql & 04_populate_dw.sql]
+------------------------------------------------------------------------+
|                         DATA WAREHOUSE LAYER                           |
| Schema: dw (Snowflake Schema + Bridge Table)                           |
| - Fact: dw.fact_movie_performance                                      |
| - Dimensions: dw.dim_time, dw.dim_geography, dw.dim_director           |
| - Hierarchy: dw.dim_macro_genre -> dw.dim_genre                        |
| - Bridge: dw.bridge_movie_genre                                        |
+------------------------------------------------------------------------+
                    |                                  |
                    v [04_export_charts.py]            v [05_run_quality_checks.py]
+---------------------------------------+   +----------------------------+
|        ANALYTICS & VISUALIZATIONS     |   |    DATA QUALITY ASSURANCE  |
| 6 Publication-Ready Charts            |   | Automated SQL Verifications|
| (Saved to deliverables/charts/)       |   | (Foreign Keys, Logic, Rng) |
+---------------------------------------+   +----------------------------+
```

---

## Data Sources

| Source | File Name | Format | Primary Role & Extracted Attributes |
|---|---|---|---|
| **Kaggle** | `movies_metadata.csv` | CSV | Budget, revenue, TMDB rating (`vote_average`), vote count, production countries JSON, release status |
| **Kaggle** | `links.csv` | CSV | Key mapping between TMDB identifiers (`tmdbId`) and IMDb identifiers (`imdbId`) |
| **Kaggle** | `credits.csv` | CSV | Cast and crew metadata |
| **Kaggle** | `keywords.csv` | CSV | Movie plot keywords |
| **IMDb** | `title.basics.tsv` | TSV | Canonical title ID (`tconst`), primary title, release year, runtime minutes, genres |
| **IMDb** | `title.ratings.tsv` | TSV | Weighted IMDb average rating (`averageRating`), total number of votes (`numVotes`) |
| **IMDb** | `title.crew.tsv` | TSV | Director identifiers (`directors`) and writer identifiers |
| **IMDb** | `name.basics.tsv` | TSV | Director names (`primaryName`), birth year, death year |

---

## Dimensional Modeling

The warehouse design is documented in [deliverables/DFM.JPEG](deliverables/DFM.JPEG) and [deliverables/SnowFlake.png](deliverables/SnowFlake.png).

### Fact Table: `dw.fact_movie_performance`
- **Granularity**: One row per distinct movie.
- **Measures & Numeric Attributes**:
  - `budget`: Production budget in USD.
  - `revenue`: Box office gross revenue in USD.
  - `profit`: Calculated net profit ($Revenue - Budget$).
  - `runtime`: Film runtime in minutes.
  - `imdb_rating`: IMDb average rating (1.0 to 10.0 scale).
  - `imdb_votes`: Total user votes recorded on IMDb.
  - `tmdb_rating`: TMDB average score (1.0 to 10.0 scale).
  - `tmdb_votes`: Total user votes recorded on TMDB.
- **Foreign Keys**: `time_key`, `geo_key`, `director_key`.

### Dimension Tables
- **`dw.dim_time`**: Temporal analysis based on release dates (`release_year`, `decade` formatted as `'1990s'`).
- **`dw.dim_geography`**: Spatial analysis derived from primary production country (`country_code`, `country_name`, `continent`).
- **`dw.dim_director`**: Primary director details (`director_id`, `director_name`, `birth_year`, `death_year`).
- **`dw.dim_macro_genre` & `dw.dim_genre` (Snowflake Hierarchy)**:
  - Normalizes genres into broader categories (`'Narrative & Drama'`, `'Action & Adventure'`, `'Comedy & Family'`, `'Horror & Thriller'`, `'Other'`).
- **`dw.bridge_movie_genre` (Bridge Table)**:
  - Connects `dw.fact_movie_performance` with `dw.dim_genre` to resolve the multi-valued nature of movie genres.

---

## Repository Structure

```text
DW-Proj/
│
├── database/
│   └── ddl/
│       ├── 01_init_schemas.sql       # Creates staging, reconciled, and dw schemas
│       ├── 02_reconciled_layer.sql   # Reconciles, cleanses, and unrolls staging data
│       ├── 03_create_dw_schema.sql   # Creates Fact, Dimension, and Bridge tables
│       ├── 04_populate_dw.sql        # Populates the Snowflake schema from reconciled tables
│       └── 05_quality_checks.sql     # Automated integrity and consistency queries
│
├── etl_pipeline/
│   ├── 01_extract.py                 # Chunked loader from CSV/TSV to staging schema
│   ├── 02_reconcile.py               # Executes 02_reconciled_layer.sql
│   ├── 03_build_dw.py                # Executes 03_create_dw_schema.sql & 04_populate_dw.sql
│   ├── 04_export_charts.py           # Runs OLAP queries and generates analytical charts
│   └── 05_run_quality_checks.py      # Executes data quality test suite
│
├── deliverables/
│   ├── DFM.JPEG                      # Dimensional Fact Model diagram
│   ├── SnowFlake.png                 # Snowflake Schema relational diagram
│   ├── presentation.pdf              # Slide deck presenting the project and findings
│   └── charts/                       # Generated publication-quality analytical charts
│       ├── 01_profit_by_genre.png
│       ├── 02_decade_trends.png
│       ├── 03_rating_comparison.png
│       ├── 04_continent_performance.png
│       ├── 05_runtime_impact.png
│       └── 06_votes_vs_profit.png
│
├── run_pipeline.py                   # Master orchestrator for pipeline execution
├── requirements.txt                  # Python dependencies
├── .env                              # Database connection credentials (local)
└── README.md                         # Project documentation
```

---

## Steps to Reproduce the Pipeline

Follow these step-by-step instructions to set up the environment, database, and execute the complete pipeline.

### 1. Prerequisites

- **Python**: Version 3.10 or higher.
- **PostgreSQL**: Version 14 or higher running locally or accessible via network.
- **Disk Space**: At least 10–15 GB of free space if ingesting the full raw IMDb and Kaggle datasets.

### 2. Clone and Setup Environment

Clone the repository and create a Python virtual environment:

```bash
# Navigate to the repository root
cd DW-Proj

# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
# On macOS / Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install required dependencies
pip install -r requirements.txt
```

### 3. Database Configuration

Create a PostgreSQL database (e.g. named `movie_analytics_dw`):

```bash
createdb -U postgres movie_analytics_dw
```
*(Or create it via `psql`: `CREATE DATABASE movie_analytics_dw;`)*

Create a `.env` file in the root directory `DW-Proj/` with your database credentials:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=movie_analytics_dw
DB_USER=postgres
DB_PASSWORD=your_postgres_password
```

### 4. Schema Initialization

Initialize the three PostgreSQL schemas (`staging`, `reconciled`, `dw`):

```bash
psql -U postgres -d movie_analytics_dw -f database/ddl/01_init_schemas.sql
```

### 5. Dataset Preparation

Ensure the source datasets are organized under the `datasets/` folder structure:

```text
DW-Proj/
└── datasets/
    ├── source_kaggle/
    │   ├── links.csv
    │   ├── movies_metadata.csv
    │   ├── credits.csv
    │   └── keywords.csv
    └── source_imdb/
        ├── title.basics.tsv
        ├── title.ratings.tsv
        ├── title.crew.tsv
        └── name.basics.tsv
```

> **Data download links**:
> - Kaggle: [The Movies Dataset](https://www.kaggle.com/datasets/rounakbanik/the-movies-dataset)
> - IMDb: [IMDb Non-Commercial Datasets](https://developer.imdb.com/non-commercial-datasets/)

### 6. Staging Data Extraction

Load the raw files into the `staging` schema using chunked ingestion (configured to 100,000 rows per batch to preserve memory):

```bash
python etl_pipeline/01_extract.py
```

*Note: Ingesting the multi-gigabyte IMDb datasets may take several minutes depending on hardware and disk speed.*

### 7. Run the End-to-End Pipeline

Once staging data is populated, run the automated pipeline runner:

```bash
python run_pipeline.py
```

This master script automatically executes the entire transformation, warehousing, analytics, and validation workflow in sequence:
1. **Reconciliation Layer**: Cleans dirty attributes, extracts geography and JSON structures, unrolls directors and genres.
2. **DW Schema & Population**: Builds dimension, fact, and bridge tables and loads clean data into the Snowflake schema.
3. **Analytics Export**: Queries the warehouse and exports all 6 visualization charts into `deliverables/charts/`.
4. **Quality Checks**: Executes automated tests to verify schema and data integrity.

---

### Alternative: Step-by-Step Execution

You can also run each pipeline phase individually:

```bash
# Step 1: Populate Reconciled Layer
python etl_pipeline/02_reconcile.py

# Step 2: Create DW Schema and Populate Snowflake Tables
python etl_pipeline/03_build_dw.py

# Step 3: Run OLAP Queries & Export Charts
python etl_pipeline/04_export_charts.py

# Step 4: Run Data Quality Checks
python etl_pipeline/05_run_quality_checks.py
```

---

## Analytical Insights & Visualizations

The script `etl_pipeline/04_export_charts.py` queries the warehouse schema to answer strategic questions and saves the figures into `deliverables/charts/`:

1. **Top Most Profitable Genres** (`01_profit_by_genre.png`):
   - Computes average net profit (in Millions USD) across film genres with a minimum threshold of 50 releases.
   - Highlights high-return categories (e.g., Animation, Adventure, Family).
2. **Financial Evolution Across Decades** (`02_decade_trends.png`):
   - Traces the progression of average production budget, gross revenue, and profit from the 1950s through the 2010s.
   - Illustrates the exponential growth of blockbuster production budgets and global revenues.
3. **IMDb vs TMDB Rating Divergence** (`03_rating_comparison.png`):
   - Compares perception across platforms grouped by budget tier (*Blockbuster* $\ge \$100M$, *Mid Budget* $\$30M-\$100M$, *Low Budget* $< \$30M$).
   - Reveals divergence in audience scoring behaviors between platforms.
4. **Movie Volume vs Average Rating Across Continents** (`04_continent_performance.png`):
   - Dual-axis analysis showing volume of production alongside average IMDb score per continent.
5. **Runtime Impact on Profitability & Critical Reception** (`05_runtime_impact.png`):
   - Examines performance categorized into runtime tiers (*Short* $<90\text{m}$, *Standard* $90-120\text{m}$, *Long* $121-150\text{m}$, *Epic* $>150\text{m}$).
6. **IMDb Votes vs Profit Correlation** (`06_votes_vs_profit.png`):
   - Regression analysis examining audience engagement (vote count) against commercial financial profit.

---

## Automated Data Quality Assurance

The test suite in `05_quality_checks.sql` (executed by `05_run_quality_checks.py`) enforces strict validation criteria:

| Quality Check | Objective | Expected Result |
|---|---|---|
| **Orphan Foreign Keys** | Ensures `time_key`, `geo_key`, and `director_key` in `fact_movie_performance` reference valid dimension records. | 0 failures |
| **Bridge Table Integrity** | Asserts no dangling references exist between `bridge_movie_genre`, `fact_movie_performance`, and `dim_genre`. | 0 failures |
| **Financial Consistency** | Validates that $Profit = Revenue - Budget$ holds for every fact record with complete monetary values. | 0 failures |
| **Domain Range Validity** | Ensures all IMDb and TMDB ratings fall strictly within the valid range $[1.0, 10.0]$. | 0 failures |

Output summary:
```text
Running Data Quality Checks on Data Warehouse...
[PASS] Orphan time keys: 0 failures
[PASS] Orphan geography keys: 0 failures
[PASS] Orphan director keys: 0 failures
[PASS] Bridge table orphan facts: 0 failures
[PASS] Bridge table orphan genres: 0 failures
[PASS] Financial calculation inconsistencies: 0 failures
[PASS] Invalid IMDb rating range: 0 failures
[PASS] Invalid TMDB rating range: 0 failures
--------------------------------------------------
All Quality Checks passed successfully.
```

---

## Project Deliverables

- **[presentation.pdf](deliverables/presentation.pdf)**: Complete academic slide presentation summarizing project methodology, architecture, and analytical outcomes.
- **[DFM.JPEG](deliverables/DFM.JPEG)**: Conceptual schema design showing facts, dimensions, hierarchies, and measures.
- **[SnowFlake.png](deliverables/SnowFlake.png)**: Logical relational database diagram of the deployed Snowflake schema.
- **[charts/](deliverables/charts/)**: High-resolution PNG figures generated directly by OLAP queries.
