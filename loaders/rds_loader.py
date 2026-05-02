import os
import logging
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from dotenv import load_dotenv

load_dotenv()

# ── Logging Setup ──────────────────────────────────────────
logger = logging.getLogger(__name__)

# ── Database Connection ────────────────────────────────────
def get_engine():
    """
    Creates a SQLAlchemy engine from environment variables.
    Raises a clear error if credentials are missing.
    """
    db_host = os.getenv("DB_HOST",     "localhost")
    db_port = os.getenv("DB_PORT",     "5432")
    db_name = os.getenv("DB_NAME",     "gipc_platform")
    db_user = os.getenv("DB_USER",     "postgres")
    db_pass = os.getenv("DB_PASSWORD", "")

    if not db_pass:
        raise ValueError("DB_PASSWORD is not set in your .env file")

    url = f"postgresql+psycopg2://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
    return create_engine(url)


# ── Load Function ──────────────────────────────────────────
def load(df: pd.DataFrame) -> bool:
    """
    Loads a clean DataFrame into the economic_indicators table.
    Returns True on success, False on failure.
    """
    if df.empty:
        logger.error("DataFrame is empty — nothing to load")
        return False

    try:
        engine = get_engine()
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        return False

    # Test connection
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database connection successful")
    except OperationalError as e:
        logger.error(f"Cannot connect to database: {e}")
        logger.error("Check that PostgreSQL is running and your .env credentials are correct")
        return False

    # Stage the data
    try:
        df.to_sql(
            name="economic_indicators_staging",
            con=engine,
            if_exists="replace",
            index=False,
            method="multi",
        )
        logger.info(f"Staged {len(df)} records")
    except SQLAlchemyError as e:
        logger.error(f"Failed to write staging table: {e}")
        return False

    # Upsert from staging to main table
    try:
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
            logger.info(f"Rows inserted: {result.rowcount}")

    except SQLAlchemyError as e:
        logger.error(f"Upsert failed: {e}")
        return False

    # Clean up staging
    try:
        with engine.begin() as conn:
            conn.execute(text("DROP TABLE IF EXISTS economic_indicators_staging"))
        logger.info("Staging table cleaned up")
    except SQLAlchemyError as e:
        logger.warning(f"Could not drop staging table: {e}")

    return True


# ── Export Function ────────────────────────────────────────
def export_csv(df: pd.DataFrame, output_dir: str = "exports") -> str | None:
    """
    Exports the clean DataFrame to a timestamped CSV file.
    Returns the filepath on success, None on failure.
    """
    from datetime import datetime

    if df.empty:
        logger.error("DataFrame is empty — nothing to export")
        return None

    try:
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename  = f"gipc_economic_indicators_{timestamp}.csv"
        filepath  = os.path.join(output_dir, filename)

        df.to_csv(filepath, index=False)
        logger.info(f"CSV exported: {filepath}")
        logger.info(f"Rows: {len(df)} | Columns: {list(df.columns)}")
        return filepath

    except OSError as e:
        logger.error(f"Failed to write CSV: {e}")
        return None


# ── Run Function ───────────────────────────────────────────
def run(df: pd.DataFrame) -> bool:
    logger.info("=== Load started ===")
    success = load(df)
    if success:
        logger.info("=== Load complete ===")
    else:
        logger.error("=== Load failed ===")
    return success


# ── Entry Point ────────────────────────────────────────────
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[
            logging.FileHandler("pipeline.log", encoding="utf-8"),
            logging.StreamHandler()
        ]
    )

    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    from extractors.world_bank  import run as wb_run
    from extractors.imf         import run as imf_run
    from transformers.normalize import run as transform_run

    logger.info("Pipeline started")

    wb_data  = wb_run()
    imf_data = imf_run()

    df = transform_run(wb_data, imf_data)

    success = run(df)

    if success:
        export_csv(df)
        logger.info("Pipeline finished successfully")
    else:
        logger.error("Pipeline finished with errors — check pipeline.log")