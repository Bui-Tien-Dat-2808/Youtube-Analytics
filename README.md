# YouTube Data Pipeline & Analytics Platform

Portfolio project for a Data Engineer Intern role. The platform ingests recent YouTube videos, stores raw and clean layers in Apache Iceberg, loads a star-schema warehouse into PostgreSQL, builds analytics models with dbt, orchestrates workloads with Airflow, and exposes metrics to Superset.

## Architecture

The project follows Clean Architecture to keep orchestration, business logic, and infrastructure concerns isolated.

```text
.
|-- application/
|   `-- services/
|-- dbt/
|   `-- models/
|-- domain/
|   |-- entities/
|   `-- use_cases/
|-- infrastructure/
|   |-- database/
|   |-- iceberg/
|   `-- youtube_api/
|-- interfaces/
|   `-- airflow/
|-- shared/
|   |-- config/
|   `-- logging/
|-- docker/
|-- data/
|-- docker-compose.yaml
`-- .env.example
```

### Layer responsibilities

- `domain`: entities and use cases.
- `application`: service orchestration without framework concerns.
- `infrastructure`: YouTube API adapter, Iceberg access, Spark processing, PostgreSQL loading.
- `interfaces`: Airflow DAG and task wrappers.
- `shared`: configuration and centralized logging.

## End-to-end pipeline

1. `fetch_youtube_data`
   Resolves top trending keywords from Google Trends RSS by region.
   Uses YouTube Data API v3 to search videos for each keyword.
   Restricts extraction to the latest 7 days.
   Uses the latest `published_at` in the raw Iceberg table as the incremental watermark.
   Persists the fetched batch to a local staging artifact.
2. `load_raw_iceberg`
   Loads the staged batch into the raw Iceberg table.
3. `process_clean_data`
   Reads raw Iceberg data with PySpark.
   Removes null records.
   Normalizes text to lowercase and removes special characters.
   Converts timestamps to UTC.
   Validates numeric columns.
   Removes duplicates by `video_id` and `keyword`.
   Writes the clean layer back to Iceberg in Parquet-backed tables.
4. `load_to_postgres`
   Reads the clean Iceberg table.
   Loads `dim_channel`, `dim_keyword`, `fact_video`, and `bridge_video_keyword` to PostgreSQL using Spark JDBC.
5. `run_dbt_models`
   Builds analytics-ready mart models for Superset.

## Data model

### Iceberg

- Raw table: `${ICEBERG_RAW_TABLE}`
- Clean table: `${ICEBERG_CLEAN_TABLE}`
- Catalog: Hadoop catalog
- Partitioning:
  - Raw: `days(published_at), channel_id`
  - Clean: `publish_date, channel_id`

### PostgreSQL star schema

- `analytics.dim_channel(channel_id, channel_name)`
- `analytics.fact_video(video_id, channel_id, publish_date, views, likes, comments)`
- `analytics.dim_keyword(keyword_name)`
- `analytics.bridge_video_keyword(video_id, keyword_name)`

### dbt marts

- `marts.top_videos_by_views`
- `marts.video_count_by_day`
- `marts.top_channels_by_engagement`
- `marts.top_keywords_by_total_views`

## Superset dashboard suggestion

Create a PostgreSQL connection in Superset:

- SQLAlchemy URI:
  `postgresql+psycopg2://youtube:youtube@postgres:5432/youtube_analytics`

Recommended charts:

- Time-series line chart on `marts.video_count_by_day`
- Bar chart on `marts.top_channels_by_engagement`
- Table or bar chart on `marts.top_videos_by_views`

## Run locally

### 1. Configure environment

```bash
cp .env.example .env
```

Set `YOUTUBE_API_KEY`, then configure keyword discovery:

- `YOUTUBE_KEYWORD_SOURCE=google_trends_rss`
- `YOUTUBE_TRENDS_GEO=US`
- `YOUTUBE_TOP_KEYWORDS_LIMIT=10`
- `YOUTUBE_KEYWORD_FALLBACK=data engineering,machine learning,analytics engineering`

### 2. Start services

```bash
docker compose up --build airflow-init
docker compose up --build -d
```

### 3. Trigger the pipeline

- Open Airflow at `http://localhost:8080`
- Enable DAG `youtube_analytics_pipeline`
- Trigger manually or wait for the 3-hour schedule

### 4. Run dbt manually if needed

```bash
docker compose exec dbt dbt debug --project-dir /opt/project/dbt --profiles-dir /opt/project/dbt
docker compose exec dbt dbt run --project-dir /opt/project/dbt --profiles-dir /opt/project/dbt
```

### 5. Open Superset

- URL: `http://localhost:8088`
- Use the credentials from `.env`

## Logging

All modules use the shared logger in `shared/logging/logger.py`. Logging is enabled for:

- YouTube API fetch
- Iceberg writes
- Spark cleaning
- PostgreSQL loading
- dbt execution

## Important implementation notes

- No `print` statements are used. Observability relies on Python logging.
- Configuration is environment-driven through `pydantic-settings`.
- Business logic stays out of the Airflow DAG.
- Spark JDBC is used for loading the warehouse, not `pandas.to_sql`.
- The warehouse load is idempotent by truncating target tables and reloading from the clean layer.