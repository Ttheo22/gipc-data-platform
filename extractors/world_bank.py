import requests

# ------Configuration ---------------------
COUNTRY_CODE = "GH"  # Ghana
BASE_URL = "https://api.worldbank.org/v2"
YEARS = 20 # how many years of data to fetch

INDICATORS = {
    # Macroeconomic
    "gdp_current_usd":        "NY.GDP.MKTP.CD",
    "gdp_growth_rate":        "NY.GDP.MKTP.KD.ZG",
    "inflation_cpi":          "FP.CPI.TOTL.ZG",
    "population":             "SP.POP.TOTL",

    # FDI (UNCTAD data served via World Bank)
    "fdi_net_inflows_usd":    "BX.KLT.DINV.CD.WD",
    "fdi_net_outflows_usd":   "BM.KLT.DINV.CD.WD",

    # Trade
    "exports_usd":            "NE.EXP.GNFS.CD",
    "imports_usd":            "NE.IMP.GNFS.CD",
    "trade_percent_gdp":      "NE.TRD.GNFS.ZS",

    # Development
    "gni_per_capita":         "NY.GNP.PCAP.CD",
    "unemployment_rate":      "SL.UEM.TOTL.ZS",
    "internet_users_percent": "IT.NET.USER.ZS",
}

# -----------Fetch Function----------------------------
def fetch_indicator(indicator_code: str, indicator_name: str) -> list[dict]:
    """Fetches data for a single Wold Bank indicator for Ghana.
    Returns a list of yearly records.
    """
    url =(
        f"{BASE_URL}/country/{COUNTRY_CODE}"
        f"/indicator/{indicator_code}"
        f"?format=json&per_page={YEARS}"
    )

    print(f"Fetching {indicator_name} from: {url}")

    response = requests.get(url, timeout=10)
    response.raise_for_status()  # raises an error if request failed

    raw = response.json()

    # World Bank returns a list of 2 items:
    # [0] = metadata, [1] = actual data
    records = raw[1]

    results = []
    for record in records:
        results.append({
            "indicator_name": indicator_name,
            "indicator_code": indicator_code,
            "country":        record["country"]["value"],
            "year":           record["date"],
            "value":          record["value"],
        })

    return results


# ── Run Function ───────────────────────────────────────────
def run() -> list[dict]:
    """
    Loops through all indicators and returns all records combined.
    """
    all_data = []

    for name, code in INDICATORS.items():
        records = fetch_indicator(code, name)
        all_data.extend(records)
        print(f"  → {len(records)} records fetched for {name}")

    print(f"\nTotal records fetched: {len(all_data)}")
    return all_data


# ── Entry Point ────────────────────────────────────────────
if __name__ == "__main__":
    data = run()

    # Print first 3 records so we can see what came back
    print("\nSample output:")
    for record in data[:3]:
        print(record)