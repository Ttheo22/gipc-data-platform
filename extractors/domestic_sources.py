import os
import glob
import logging
import pandas as pd

# ── Logging Setup ──────────────────────────────────────────
logger = logging.getLogger(__name__)

# ── Configuration ──────────────────────────────────────────
BASE_DIR = "data/manual_uploads"

SOURCE_CONFIG = {
    "gss": {
        "path":    os.path.join(BASE_DIR, "gss"),
        "source":  "GSS",
        "country": "Ghana",
    },
    "bog": {
        "path":    os.path.join(BASE_DIR, "bog"),
        "source":  "BoG",
        "country": "Ghana",
    },
    "mof": {
        "path":    os.path.join(BASE_DIR, "mof"),
        "source":  "MoF",
        "country": "Ghana",
    },
}

# ── Fetch Function ─────────────────────────────────────────
def fetch_source(source_key: str, config: dict) -> list[dict]:
    """
    Reads all CSV files from a source folder.
    Validates required columns and returns structured records.
    """
    folder  = config["path"]
    source  = config["source"]
    country = config["country"]

    # Find all CSV files in the folder
    csv_files = glob.glob(os.path.join(folder, "*.csv"))

    if not csv_files:
        logger.warning(f"No CSV files found in {folder} — skipping {source}")
        return []

    logger.info(f"Found {len(csv_files)} file(s) for {source}")

    all_records = []

    for filepath in csv_files:
        filename = os.path.basename(filepath)
        logger.info(f"  Reading {filename}")

        try:
            df = pd.read_csv(filepath)
        except Exception as e:
            logger.error(f"  Could not read {filename}: {e} — skipping")
            continue

        # Validate required columns
        required = ["indicator_name", "value"]
        missing  = [col for col in required if col not in df.columns]
        if missing:
            logger.error(f"  {filename} missing columns: {missing} — skipping")
            continue

        # Normalise column names
        df.columns = [col.lower().strip() for col in df.columns]

        # Drop rows with no value
        before = len(df)
        df = df.dropna(subset=["value"])
        dropped = before - len(df)
        if dropped:
            logger.warning(f"  Dropped {dropped} rows with null values in {filename}")

        for _, row in df.iterrows():
            record = {
                "indicator_name": row.get("indicator_name"),
                "source":         source,
                "country":        country,
                "value":          row.get("value"),
                "unit":           row.get("unit", "unknown"),
                "notes":          row.get("notes", ""),
            }

            # Handle year — some sources have year+quarter, some year+month
            year = row.get("year")
            if pd.notna(row.get("quarter", None)):
                record["year"]    = str(int(year))
                record["quarter"] = row.get("quarter")
                record["period"]  = f"{int(year)} {row.get('quarter')}"
            elif pd.notna(row.get("month", None)):
                record["year"]   = str(int(year))
                record["month"]  = row.get("month")
                record["period"] = f"{row.get('month')} {int(year)}"
            else:
                record["year"]   = str(int(year))
                record["period"] = str(int(year))

            all_records.append(record)

    logger.info(f"  -> {len(all_records)} total records from {source}")
    return all_records


# ── Run Function ───────────────────────────────────────────
def run() -> list[dict]:
    """
    Reads all manual upload folders and returns combined records.
    """
    all_data  = []
    failed    = []
    succeeded = []

    logger.info("=== Domestic sources extraction started ===")

    for key, config in SOURCE_CONFIG.items():
        records = fetch_source(key, config)
        if records:
            all_data.extend(records)
            succeeded.append(config["source"])
        else:
            failed.append(config["source"])

    logger.info("=== Domestic sources extraction complete ===")
    logger.info(f"  Succeeded : {succeeded}")
    logger.info(f"  Failed    : {failed}")
    logger.info(f"  Total records: {len(all_data)}")

    return all_data


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
    data = run()

    print("\nSample output:")
    for record in data[:3]:
        print(record)