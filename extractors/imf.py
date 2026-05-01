import requests

# ── Configuration ──────────────────────────────────────────
COUNTRY_CODE = "GHA"  # IMF DataMapper uses 3-letter codes
BASE_URL = "https://www.imf.org/external/datamapper/api/v1"

INDICATORS = {
    "gdp_current_usd":       "NGDPD",
    "gdp_growth_rate":       "NGDP_RPCH",
    "inflation_rate":        "PCPIPCH",
    "current_account_usd":   "BCA",
    "government_debt_gdp":   "GGXWDG_NGDP",
}

# ── Fetch Function ─────────────────────────────────────────
def fetch_indicator(indicator_name: str, indicator_code: str) -> list[dict]:
    """
    Fetches a single IMF indicator for Ghana using the DataMapper API.
    """
    url = f"{BASE_URL}/{indicator_code}/{COUNTRY_CODE}"

    print(f"Fetching {indicator_name} from: {url}")

    response = requests.get(url, timeout=15)
    response.raise_for_status()

    raw = response.json()

    # Navigate to the data
    try:
        yearly_data = raw["values"][indicator_code][COUNTRY_CODE]
    except (KeyError, TypeError):
        print(f"  ⚠ No data found for {indicator_name}")
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

    return results


# ── Run Function ───────────────────────────────────────────
def run() -> list[dict]:
    """
    Loops through all IMF indicators and returns combined records.
    """
    all_data = []

    for name, code in INDICATORS.items():
        records = fetch_indicator(name, code)
        all_data.extend(records)
        print(f"  → {len(records)} records fetched for {name}")

    print(f"\nTotal records fetched: {len(all_data)}")
    return all_data


# ── Entry Point ────────────────────────────────────────────
if __name__ == "__main__":
    data = run()

    print("\nSample output:")
    for record in data[:3]:
        print(record)