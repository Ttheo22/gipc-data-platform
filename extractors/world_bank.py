import requests
import logging

# ── Logging Setup ──────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("pipeline.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ── Configuration ──────────────────────────────────────────
COUNTRY_CODE = "GH"
BASE_URL      = "https://api.worldbank.org/v2"
YEARS         = 30
MAX_RETRIES   = 3

INDICATORS = {
    # Macroeconomic
    "gdp_current_usd":        "NY.GDP.MKTP.CD",
    "gdp_growth_rate":        "NY.GDP.MKTP.KD.ZG",
    "inflation_cpi":          "FP.CPI.TOTL.ZG",
    "population":             "SP.POP.TOTL",
    "gni_per_capita":         "NY.GNP.PCAP.CD",

    # FDI
    "fdi_net_inflows_usd":    "BX.KLT.DINV.CD.WD",
    "fdi_net_outflows_usd":   "BM.KLT.DINV.CD.WD",

    # Trade
    "exports_usd":            "NE.EXP.GNFS.CD",
    "imports_usd":            "NE.IMP.GNFS.CD",
    "trade_percent_gdp":      "NE.TRD.GNFS.ZS",

    # Development & Labour
    "unemployment_rate":      "SL.UEM.TOTL.ZS",
    "internet_users_percent": "IT.NET.USER.ZS",

    # Aid
    "oda_received_usd":       "DT.ODA.ALLD.CD",
}

# ── Fetch Function ─────────────────────────────────────────
def fetch_indicator(indicator_code: str, indicator_name: str) -> list[dict]:
    """
    Fetches a single World Bank indicator for Ghana.
    Retries up to MAX_RETRIES times on timeout.
    Returns empty list on failure so pipeline continues.
    """
    url = (
        f"{BASE_URL}/country/{COUNTRY_CODE}"
        f"/indicator/{indicator_code}"
        f"?format=json&per_page={YEARS}"
    )

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logger.info(f"Fetching {indicator_name} (attempt {attempt})")
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            raw     = response.json()
            records = raw[1]

            if not records:
                logger.warning(f"No records returned for {indicator_name}")
                return []

            results = []
            for record in records:
                results.append({
                    "indicator_name": indicator_name,
                    "indicator_code": indicator_code,
                    "country":        record["country"]["value"],
                    "year":           record["date"],
                    "value":          record["value"],
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

        except (KeyError, IndexError, TypeError) as e:
            logger.error(f"Unexpected response structure for {indicator_name}: {e} — skipping")
            return []

        except Exception as e:
            logger.error(f"Unexpected error for {indicator_name}: {e} — skipping")
            return []

    return []


# ── Run Function ───────────────────────────────────────────
def run() -> list[dict]:
    """
    Loops through all indicators.
    Continues even if individual indicators fail.
    Returns summary of successes and failures.
    """
    all_data  = []
    failed    = []
    succeeded = []

    logger.info("=== World Bank extraction started ===")

    for name, code in INDICATORS.items():
        records = fetch_indicator(code, name)
        if records:
            all_data.extend(records)
            succeeded.append(name)
        else:
            failed.append(name)

    logger.info(f"=== World Bank extraction complete ===")
    logger.info(f"  Succeeded : {len(succeeded)} indicators")
    logger.info(f"  Failed    : {len(failed)} indicators")
    if failed:
        logger.warning(f"  Failed indicators: {failed}")
    logger.info(f"  Total records: {len(all_data)}")

    return all_data


# ── Entry Point ────────────────────────────────────────────
if __name__ == "__main__":
    data = run()
    print("\nSample output:")
    for record in data[:3]:
        print(record)