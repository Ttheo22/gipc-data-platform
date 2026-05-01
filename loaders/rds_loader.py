import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

# ── Database Connection ────────────────────────────────────
def get_engine():
    """
    Creates a SQLAlchemy engine from environment variables.
    """
    db_host = os.getenv("DB_HOST",     "localhost")
    db_port = os.getenv("DB_PORT",     "5432")
    db_name = os.getenv("DB_NAME",     "gipc_platform")
    db_user = os.getenv("DB_USER",     "postgres")
    db_pass = os.getenv("DB_PASSWORD", "")

    url = f"postgresql+psycopg2://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
    return create_engine(url)


# ── Load Function ──────────────────────────────────────────
def load(df: pd.DataFrame) -> None:
    """
    Loads a clean DataFrame into the economic_indicators table.
    Uses upsert logic — skips duplicates on (indicator_name, source, country, year).
    """
    engine = get_engine()

    # Test connection first
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    print("  Database connection successful")

    # Write to a staging table first, then upsert to main table
    df.to_sql(
        name="economic_indicators_staging",
        con=engine,
        if_exists="replace",   # always replace staging
        index=False,
        method="multi",        # faster bulk insert
    )
    print(f"  Staged {len(df)} records")

    # Upsert from staging to main table
    upsert_sql = text("""
        INSERT INTO economic_indicators
            (indicator_name, source, country, year, value, unit)
        SELECT
            indicator_name, source, country, year, value, unit
        FROM
            economic_indicators_staging
        ON CONFLICT (indicator_name, source, country, year)
        DO NOTHING;
    """)

    with engine.begin() as conn:
        result = conn.execute(upsert_sql)
        print(f"  Rows inserted: {result.rowcount}")

    # Clean up staging table
    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS economic_indicators_staging"))
    print("  Staging table cleaned up")


# ── Run Function ───────────────────────────────────────────
def run(df: pd.DataFrame) -> None:
    print("\n── Loading to PostgreSQL ──────────────────────────")
    load(df)
    print("  Load complete")


# ── Entry Point ────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    from extractors.world_bank import run as wb_run
    from extractors.imf        import run as imf_run
    from transformers.normalize import run as transform_run

    print("Extracting...")
    wb_data  = wb_run()
    imf_data = imf_run()

    print("\nTransforming...")
    df = transform_run(wb_data, imf_data)

    print("\nLoading...")
    run(df)