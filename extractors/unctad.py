import pandas as pd

# ── Configuration ──────────────────────────────────────────
COUNTRY_NAME = "Ghana"
BASE_URL = "https://unctadstat.unctad.org/datacentre/getData"

# UNCTAD dataset codes
DATASETS = {
    "fdi_inflows_usd":   "US.FdiFlowsCountry",
    "fdi_outflows_usd":  "US.FdiFlowsCountry",
    "fdi_inward_stock":  "US.FdiStockCountry",
}

# ── Fetch Function ─────────────────────────────────────────
def fetch_dataset(indicator_name: str, dataset_code: str) -> list[dict]:
    """
    Fetches a UNCTAD dataset as CSV, filters for Ghana,
    and returns structured records.
    """
    url = (
        f"{BASE_URL}/{dataset_code}"
        f"?economies=GHA&format=csv"
    )

    print(f"Fetching {indicator_name} from: {url}")

    try:
        df = pd.read_csv(url)
    except Exception as e:
        print(f"  ⚠ Could not fetch {indicator_name}: {e}")
        return []

    # Show columns so we know what came back
    print(f"  Columns: {list(df.columns)}")
    print(f"  Shape: {df.shape}")

    # Filter for Ghana just in case the CSV has multiple countries
    if "Economy" in df.columns:
        df = df[df["Economy"].str.contains(COUNTRY_NAME, na=False)]
    elif "economy" in df.columns:
        df = df[df["economy"].str.contains(COUNTRY_NAME, na=False)]

    # Normalise column names to lowercase
    df.columns = [col.lower().strip() for col in df.columns]

    results = []
    for _, row in df.iterrows():
        results.append({
            "indicator_name": indicator_name,
            "dataset_code":   dataset_code,
            "country":        COUNTRY_NAME,
            "raw_row":        row.to_dict(),  # keep all columns for now
        })

    return results


# ── Run Function ───────────────────────────────────────────
def run() -> list[dict]:
    """
    Fetches all UNCTAD datasets and returns combined records.
    """
    all_data = []
    seen_datasets = set()  # avoid fetching same dataset twice

    for name, code in DATASETS.items():
        if code in seen_datasets:
            print(f"Skipping {name} — dataset {code} already fetched")
            continue

        records = fetch_dataset(name, code)
        all_data.extend(records)
        seen_datasets.add(code)
        print(f"  → {len(records)} records fetched for {name}\n")

    print(f"Total records fetched: {len(all_data)}")
    return all_data


# ── Entry Point ────────────────────────────────────────────
if __name__ == "__main__":
    data = run()

    print("\nSample output:")
    for record in data[:2]:
        print(record)