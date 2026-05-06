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


# ── Load Function (World Bank + IMF) ──────────────────────
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


# ── Domestic Sources Load Function ────────────────────────
def load_domestic(records: list[dict]) -> bool:
    """
    Loads domestic source records (GSS, BoG, MoF) into
    the domestic_indicators table.
    """
    if not records:
        logger.error("No domestic records to load")
        return False

    try:
        engine = get_engine()
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        return False

    try:
        df = pd.DataFrame(records)

        # Ensure year is integer
        df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")

        # Select only columns that exist in the table
        columns = [
            "indicator_name", "source", "country",
            "year", "period", "quarter", "month",
            "value", "unit", "notes"
        ]
        for col in columns:
            if col not in df.columns:
                df[col] = None

        df = df[columns]

        # Stage it
        df.to_sql(
            name="domestic_indicators_staging",
            con=engine,
            if_exists="replace",
            index=False,
            method="multi",
        )
        logger.info(f"  Staged {len(df)} domestic records")

        # Upsert
        upsert_sql = text("""
            INSERT INTO domestic_indicators
                (indicator_name, source, country, year, period,
                 quarter, month, value, unit, notes)
            SELECT
                indicator_name, source, country, year, period,
                quarter, month, value, unit, notes
            FROM
                domestic_indicators_staging
            ON CONFLICT (indicator_name, source, country, period)
            DO NOTHING;
        """)

        with engine.begin() as conn:
            result = conn.execute(upsert_sql)
            logger.info(f"  Domestic rows inserted: {result.rowcount}")

        # Cleanup
        with engine.begin() as conn:
            conn.execute(text("DROP TABLE IF EXISTS domestic_indicators_staging"))
        logger.info("  Domestic staging table cleaned up")

        return True

    except Exception as e:
        logger.error(f"Domestic load failed: {e}")
        return False


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

    from extractors.world_bank       import run as wb_run
    from extractors.imf              import run as imf_run
    from extractors.domestic_sources import run as domestic_run
    from transformers.normalize      import run as transform_run

    logger.info("Pipeline started")

    wb_data       = wb_run()
    imf_data      = imf_run()
    domestic_data = domestic_run()

    df = transform_run(wb_data, imf_data)

    success = run(df)

    # Load domestic sources into separate table
    logger.info("=== Loading domestic sources ===")
    domestic_success = load_domestic(domestic_data)
    if domestic_success:
        logger.info("Domestic sources loaded successfully")
    else:
        logger.warning("Domestic sources load failed — check pipeline.log")

    if success:
        export_csv(df)
        logger.info("Pipeline finished successfully")
    else:
        logger.error("Pipeline finished with errors — check pipeline.log")