import requests
import logging

import os
log_path = "/tmp/pipeline.log" if os.environ.get("AWS_LAMBDA_FUNCTION_NAME") else "pipeline.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(log_path, encoding="utf-8"),
        logging.StreamHandler()
    ]
)

# ── Logging Setup ──────────────────────────────────────────
logger = logging.getLogger(__name__)

# ── Lambda-aware log path ──────────────────────────────────
_log_path = "/tmp/pipeline.log" if os.environ.get("AWS_LAMBDA_FUNCTION_NAME") else "pipeline.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(_log_path, encoding="utf-8"),
        logging.StreamHandler()
    ]
)

# ── Configuration ──────────────────────────────────────────
COUNTRY_CODE = "GHA"
BASE_URL      = "https://www.imf.org/external/datamapper/api/v1"
MAX_RETRIES   = 3

INDICATORS = {
    "gdp_current_usd":    "NGDPD",
    "gdp_growth_rate":    "NGDP_RPCH",
    "inflation_rate":     "PCPIPCH",
    "current_account_usd": "BCA",
    "government_debt_gdp": "GGXWDG_NGDP",
}

# ── Fetch Function ─────────────────────────────────────────
def fetch_indicator(indicator_name: str, indicator_code: str) -> list[dict]:
    """
    Fetches a single IMF indicator for Ghana.
    Retries up to MAX_RETRIES times on timeout.
    Returns empty list on failure so pipeline continues.
    """
    url = f"{BASE_URL}/{indicator_code}/{COUNTRY_CODE}"

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logger.info(f"Fetching {indicator_name} (attempt {attempt})")
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            raw = response.json()

            try:
                yearly_data = raw["values"][indicator_code][COUNTRY_CODE]
            except (KeyError, TypeError):
                logger.warning(f"No data found for {indicator_name} — skipping")
                return []

            results = []
            for year, value in yearly_data.items():
                results.append({
                    "indicator_name": indicator_name,
                    "indicator_code": indicator_code,
                    "country":        "Ghana",
                    "year":           year,
                    "value":          value,
                })

            logger.info(f"  -> {len(results)} records fetched for {indicator_name}")
            return results

        except requests.exceptions.Timeout:
            logger.warning(f"Timeout on {indicator_name} attempt {attempt}/{MAX_RETRIES}")
            if attempt == MAX_RETRIES:
                logger.error(f"All retries exhausted for {indicator_name} — skipping")
                return []

        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error for {indicator_name}: {e} — skipping")
            return []

        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error for {indicator_name}: {e} — skipping")
            return []

        except Exception as e:
            logger.error(f"Unexpected error for {indicator_name}: {e} — skipping")
            return []

    return []


# ── Run Function ───────────────────────────────────────────
def run() -> list[dict]:
    """
    Loops through all IMF indicators.
    Continues even if individual indicators fail.
    """
    all_data  = []
    failed    = []
    succeeded = []

    logger.info("=== IMF extraction started ===")

    for name, code in INDICATORS.items():
        records = fetch_indicator(name, code)
        if records:
            all_data.extend(records)
            succeeded.append(name)
        else:
            failed.append(name)

    logger.info("=== IMF extraction complete ===")
    logger.info(f"  Succeeded : {len(succeeded)} indicators")
    logger.info(f"  Failed    : {len(failed)} indicators")
    if failed:
        logger.warning(f"  Failed indicators: {failed}")
    logger.info(f"  Total records: {len(all_data)}")

    return all_data


# ── Entry Point ────────────────────────────────────────────
if __name__ == "__main__":
    import os
    log_path = "/tmp/pipeline.log" if os.environ.get("AWS_LAMBDA_FUNCTION_NAME") else "pipeline.log"
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[
            logging.FileHandler(log_path, encoding="utf-8"),
            logging.StreamHandler()
        ]
    )
    data = run()
    print("\nSample output:")
    for record in data[:3]:
        print(record)