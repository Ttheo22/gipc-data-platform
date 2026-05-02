import logging
import wbgapi as wb

# ── Logging Setup ──────────────────────────────────────────
logger = logging.getLogger(__name__)

# ── Configuration ──────────────────────────────────────────
COUNTRY_CODE = "GHA"   # wbgapi uses ISO3
WGI_SOURCE   = 3       # World Bank source ID for Governance Indicators

INDICATORS = {
    "political_stability":      "PV.EST",
    "rule_of_law":              "RL.EST",
    "control_of_corruption":    "CC.EST",
    "government_effectiveness": "GE.EST",
    "voice_and_accountability": "VA.EST",
}

# ── Fetch Function ─────────────────────────────────────────
def fetch_indicator(indicator_name: str, indicator_code: str) -> list[dict]:
    """
    Fetches a single WGI governance indicator for Ghana
    using the wbgapi library which handles source routing correctly.
    """
    try:
        logger.info(f"Fetching {indicator_name}")

        df = wb.data.DataFrame(
            indicator_code,
            economy=COUNTRY_CODE,
            db=WGI_SOURCE,
            numericTimeKeys=True,
        )

        if df.empty:
            logger.warning(f"No data returned for {indicator_name}")
            return []

        # wbgapi returns years as columns — transpose to rows
        df = df.T.reset_index()
        df.columns = ["year", "value"]
        df = df.dropna(subset=["value"])

        results = []
        for _, row in df.iterrows():
            results.append({
                "indicator_name": indicator_name,
                "indicator_code": indicator_code,
                "country":        "Ghana",
                "year":           str(int(row["year"])),
                "value":          row["value"],
            })

        logger.info(f"  -> {len(results)} records fetched for {indicator_name}")
        return results

    except Exception as e:
        logger.error(f"Error fetching {indicator_name}: {e} — skipping")
        return []


# ── Run Function ───────────────────────────────────────────
def run() -> list[dict]:
    all_data  = []
    failed    = []
    succeeded = []

    logger.info("=== World Bank Governance extraction started ===")

    for name, code in INDICATORS.items():
        records = fetch_indicator(name, code)
        if records:
            all_data.extend(records)
            succeeded.append(name)
        else:
            failed.append(name)

    logger.info("=== World Bank Governance extraction complete ===")
    logger.info(f"  Succeeded : {len(succeeded)} indicators")
    logger.info(f"  Failed    : {len(failed)} indicators")
    if failed:
        logger.warning(f"  Failed indicators: {failed}")
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