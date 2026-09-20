import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

# Database connection
engine = create_engine(f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}')

# Create deliverables folder
output_dir = 'deliverables/charts'
os.makedirs(output_dir, exist_ok=True)

# Set global visualization style
sns.set_theme(style="whitegrid")
plt.rcParams.update({'font.sans-serif': 'DejaVu Sans', 'font.size': 10})

def chart_1_profit_by_genre():
    print("Generating Chart 1: Average Profit by Genre...")
    query = """
    SELECT 
        g.genre_name,
        ROUND(AVG(f.profit) / 1000000, 2) AS avg_profit_millions,
        COUNT(DISTINCT f.fact_key) AS movie_count
    FROM dw.fact_movie_performance f
    JOIN dw.bridge_movie_genre b ON f.fact_key = b.fact_key
    JOIN dw.dim_genre g ON b.genre_key = g.genre_key
    WHERE f.profit IS NOT NULL AND f.budget > 0
    GROUP BY g.genre_name
    HAVING COUNT(DISTINCT f.fact_key) >= 50
    ORDER BY avg_profit_millions DESC
    LIMIT 12;
    """
    df = pd.read_sql(query, engine)
    
    plt.figure(figsize=(10, 6))
    ax = sns.barplot(data=df, x='avg_profit_millions', y='genre_name', palette='crest')
    plt.title('Top 12 Most Profitable Genres (Avg Profit in Millions USD)', fontsize=13, weight='bold')
    plt.xlabel('Average Profit ($M)')
    plt.ylabel('Genre')
    
    for p in ax.patches:
        width = p.get_width()
        ax.annotate(f'${width:.1f}M', (width, p.get_y() + p.get_height() / 2.),
                    ha='left', va='center', xytext=(5, 0), textcoords='offset points', fontsize=9)
        
    plt.tight_layout()
    plt.savefig(f'{output_dir}/01_profit_by_genre.png', dpi=300)
    plt.close()

def chart_2_decade_trends():
    print("Generating Chart 2: Financial Evolution Across Decades...")
    query = """
    SELECT 
        t.decade,
        ROUND(AVG(f.budget) / 1000000, 2) AS avg_budget_m,
        ROUND(AVG(f.revenue) / 1000000, 2) AS avg_revenue_m,
        ROUND(AVG(f.profit) / 1000000, 2) AS avg_profit_m
    FROM dw.fact_movie_performance f
    JOIN dw.dim_time t ON f.time_key = t.time_key
    WHERE t.release_year >= 1950 AND t.release_year < 2020 
      AND f.profit IS NOT NULL AND f.budget > 0
    GROUP BY t.decade
    ORDER BY t.decade ASC;
    """
    df = pd.read_sql(query, engine)
    
    plt.figure(figsize=(10, 5))
    plt.plot(df['decade'], df['avg_revenue_m'], marker='o', color='#1f77b4', label='Avg Revenue ($M)', linewidth=2)
    plt.plot(df['decade'], df['avg_budget_m'], marker='s', color='#ff7f0e', label='Avg Budget ($M)', linewidth=2)
    plt.plot(df['decade'], df['avg_profit_m'], marker='^', color='#2ca02c', label='Avg Profit ($M)', linewidth=2)
    
    plt.title('Movie Financial Evolution Across Decades (1950s - 2010s)', fontsize=13, weight='bold')
    plt.xlabel('Decade')
    plt.ylabel('Amount in Millions USD ($M)')
    plt.legend()
    plt.tight_layout()
    plt.savefig(f'{output_dir}/02_decade_trends.png', dpi=300)
    plt.close()

def chart_3_rating_comparison():
    print("Generating Chart 3: IMDb vs TMDB Rating Divergence...")
    query = """
    SELECT 
        CASE 
            WHEN budget >= 100000000 THEN 'Blockbuster (>= 100M)'
            WHEN budget >= 30000000 THEN 'Mid Budget (30M-100M)'
            WHEN budget > 0 THEN 'Low Budget (< 30M)'
        END AS budget_tier,
        ROUND(AVG(imdb_rating), 2) AS avg_imdb,
        ROUND(AVG(tmdb_rating), 2) AS avg_tmdb
    FROM dw.fact_movie_performance
    WHERE imdb_rating IS NOT NULL AND tmdb_rating IS NOT NULL AND budget > 0
    GROUP BY budget_tier
    ORDER BY avg_imdb DESC;
    """
    df = pd.read_sql(query, engine)
    
    df_melted = df.melt(id_vars='budget_tier', value_vars=['avg_imdb', 'avg_tmdb'], 
                        var_name='Platform', value_name='Rating')
    df_melted['Platform'] = df_melted['Platform'].replace({'avg_imdb': 'IMDb Rating', 'avg_tmdb': 'TMDB Rating'})
    
    plt.figure(figsize=(8, 5))
    ax = sns.barplot(data=df_melted, x='budget_tier', y='Rating', hue='Platform', palette='magma')
    plt.title('Rating Comparison by Budget Tier (IMDb vs TMDB)', fontsize=13, weight='bold')
    plt.xlabel('Budget Category')
    plt.ylabel('Average Rating (Scale 1-10)')
    plt.ylim(5.0, 7.5)
    
    for p in ax.patches:
        height = p.get_height()
        if height > 0:
            ax.annotate(f'{height:.2f}', (p.get_x() + p.get_width() / 2., height),
                        ha='center', va='bottom', xytext=(0, 3), textcoords='offset points', fontsize=9)
            
    plt.tight_layout()
    plt.savefig(f'{output_dir}/03_rating_comparison.png', dpi=300)
    plt.close()

def chart_4_continent_performance():
    print("Generating Chart 4: Volume & Rating by Continent...")
    query = """
    SELECT 
        COALESCE(g.continent, 'Unknown') AS continent,
        COUNT(f.fact_key) AS total_movies,
        ROUND(AVG(f.imdb_rating), 2) AS avg_rating
    FROM dw.fact_movie_performance f
    JOIN dw.dim_geography g ON f.geo_key = g.geo_key
    WHERE g.continent <> 'Other'
    GROUP BY g.continent
    ORDER BY total_movies DESC;
    """
    df = pd.read_sql(query, engine)
    
    fig, ax1 = plt.subplots(figsize=(9, 5))
    
    color = '#2b5c8f'
    ax1.set_xlabel('Continent')
    ax1.set_ylabel('Total Movies Produced', color=color)
    bars = ax1.bar(df['continent'], df['total_movies'], color=color, alpha=0.7, width=0.5)
    ax1.tick_params(axis='y', labelcolor=color)
    
    ax2 = ax1.twinx()
    color = '#d95f02'
    ax2.set_ylabel('Average IMDb Rating', color=color)
    ax2.plot(df['continent'], df['avg_rating'], color=color, marker='o', linewidth=2.5)
    ax2.tick_params(axis='y', labelcolor=color)
    ax2.set_ylim(5.5, 7.2)
    
    plt.title('Movie Volume vs Average IMDb Rating Across Continents', fontsize=13, weight='bold')
    plt.tight_layout()
    plt.savefig(f'{output_dir}/04_continent_performance.png', dpi=300)
    plt.close()

def chart_5_runtime_impact():
    print("Generating Chart 5: Runtime Impact on Ratings and Profit...")
    query = """
    SELECT 
        CASE 
            WHEN runtime < 90 THEN 'Short (< 90m)'
            WHEN runtime BETWEEN 90 AND 120 THEN 'Standard (90m-120m)'
            WHEN runtime BETWEEN 121 AND 150 THEN 'Long (121m-150m)'
            ELSE 'Epic (> 150m)'
        END AS runtime_tier,
        ROUND(AVG(profit) / 1000000, 2) AS avg_profit_m,
        ROUND(AVG(imdb_rating), 2) AS avg_rating
    FROM dw.fact_movie_performance
    WHERE runtime > 0 AND profit IS NOT NULL AND imdb_rating IS NOT NULL
    GROUP BY runtime_tier
    ORDER BY avg_rating ASC;
    """
    df = pd.read_sql(query, engine)
    
    fig, ax1 = plt.subplots(figsize=(9, 5))
    
    color = '#17becf'
    ax1.set_xlabel('Runtime Tier')
    ax1.set_ylabel('Average Profit ($M)', color=color)
    bars = ax1.bar(df['runtime_tier'], df['avg_profit_m'], color=color, alpha=0.7, width=0.5)
    ax1.tick_params(axis='y', labelcolor=color)
    
    ax2 = ax1.twinx()
    color = '#d62728'
    ax2.set_ylabel('Average IMDb Rating', color=color)
    ax2.plot(df['runtime_tier'], df['avg_rating'], color=color, marker='s', linewidth=2.5)
    ax2.tick_params(axis='y', labelcolor=color)
    
    plt.title('Movie Runtime Impact on Profit and IMDb Rating', fontsize=13, weight='bold')
    plt.tight_layout()
    plt.savefig(f'{output_dir}/05_runtime_impact.png', dpi=300)
    plt.close()

def chart_6_votes_vs_profit():
    print("Generating Chart 6: Votes vs Profit Correlation...")
    query = """
    SELECT 
        imdb_votes,
        ROUND(profit / 1000000, 2) AS profit_m
    FROM dw.fact_movie_performance
    WHERE profit IS NOT NULL AND imdb_votes > 50000 AND profit > 0
    """
    df = pd.read_sql(query, engine)
    
    plt.figure(figsize=(9, 6))
    sns.regplot(data=df, x='imdb_votes', y='profit_m', 
                scatter_kws={'alpha':0.4, 'color':'#2ca02c'}, 
                line_kws={'color':'#d62728', 'linewidth':2})
    
    plt.title('Correlation: IMDb Votes vs Profit ($M) (Votes > 50k)', fontsize=13, weight='bold')
    plt.xlabel('Number of IMDb Votes')
    plt.ylabel('Profit ($M)')
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/06_votes_vs_profit.png', dpi=300)
    plt.close()

if __name__ == "__main__":
    chart_1_profit_by_genre()
    chart_2_decade_trends()
    chart_3_rating_comparison()
    chart_4_continent_performance()
    chart_5_runtime_impact()
    chart_6_votes_vs_profit()
    print(f"\nAll charts exported successfully to {output_dir}/")