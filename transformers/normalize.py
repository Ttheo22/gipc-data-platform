import pandas as pd

# ── Unit Definitions ───────────────────────────────────────
# Tells us the unit for each indicator and whether to convert
INDICATOR_UNITS = {
    # World Bank - values are raw, need converting to billions
    "gdp_current_usd":        {"unit": "USD billions", "source": "world_bank", "scale": 1e-9},
    "gdp_growth_rate":        {"unit": "percent",      "source": "world_bank", "scale": 1},
    "inflation_cpi":          {"unit": "percent",      "source": "world_bank", "scale": 1},
    "population":             {"unit": "persons",      "source": "world_bank", "scale": 1},
    "gni_per_capita":         {"unit": "USD",          "source": "world_bank", "scale": 1},
    "fdi_net_inflows_usd":    {"unit": "USD billions", "source": "world_bank", "scale": 1e-9},
    "fdi_net_outflows_usd":   {"unit": "USD billions", "source": "world_bank", "scale": 1e-9},
    "exports_usd":            {"unit": "USD billions", "source": "world_bank", "scale": 1e-9},
    "imports_usd":            {"unit": "USD billions", "source": "world_bank", "scale": 1e-9},
    "trade_percent_gdp":      {"unit": "percent",      "source": "world_bank", "scale": 1},
    "unemployment_rate":      {"unit": "percent",      "source": "world_bank", "scale": 1},
    "internet_users_percent": {"unit": "percent",      "source": "world_bank", "scale": 1},
    "oda_received_usd":       {"unit": "USD billions", "source": "world_bank", "scale": 1e-9},

    # IMF - values already in billions
    "gdp_current_usd_imf":    {"unit": "USD billions", "source": "imf",        "scale": 1},
    "gdp_growth_rate_imf":    {"unit": "percent",      "source": "imf",        "scale": 1},
    "inflation_rate":         {"unit": "percent",      "source": "imf",        "scale": 1},
    "current_account_usd":    {"unit": "USD billions", "source": "imf",        "scale": 1},
    "government_debt_gdp":    {"unit": "percent",      "source": "imf",        "scale": 1},
}

# IMF indicators that overlap with World Bank — we rename to avoid confusion
IMF_RENAME = {
    "gdp_current_usd": "gdp_current_usd_imf",
    "gdp_growth_rate": "gdp_growth_rate_imf",
}


# ── Step 1: Tag Each Record With Its Source ────────────────
def tag_source(records: list[dict], source: str) -> list[dict]:
    """
    Adds a 'source' field to every record.
    Also renames IMF indicators that overlap with World Bank.
    """
    tagged = []
    for record in records:
        record = record.copy()
        record["source"] = source

        # Rename overlapping IMF indicators
        if source == "imf" and record["indicator_name"] in IMF_RENAME:
            record["indicator_name"] = IMF_RENAME[record["indicator_name"]]

        tagged.append(record)
    return tagged


# ── Step 2: Convert to Unified Schema ─────────────────────
def to_unified_schema(record: dict) -> dict | None:
    """
    Converts a raw record to the unified schema.
    Returns None if the record should be dropped.
    """
    indicator = record.get("indicator_name")
    meta      = INDICATOR_UNITS.get(indicator)

    # Drop records for indicators not in our schema
    if meta is None:
        return None

    # Drop records with no value
    raw_value = record.get("value")
    if raw_value is None:
        return None

    # Convert types safely
    try:
        year  = int(record["year"])
        value = float(raw_value) * meta["scale"]
    except (ValueError, TypeError):
        return None

    return {
        "indicator_name": indicator,
        "source":         record.get("source", meta["source"]),
        "country":        record.get("country", "Ghana"),
        "year":           year,
        "value":          round(value, 4),
        "unit":           meta["unit"],
    }


# ── Step 3: Clean the Full Dataset ────────────────────────
def clean(records: list[dict]) -> pd.DataFrame:
    """
    Applies unified schema to all records.
    Drops nulls, deduplicates, and sorts.
    Returns a clean pandas DataFrame.
    """
    cleaned = []
    dropped = 0

    for record in records:
        result = to_unified_schema(record)
        if result is None:
            dropped += 1
        else:
            cleaned.append(result)

    print(f"  Records processed : {len(records)}")
    print(f"  Records dropped   : {dropped}  (nulls or unknown indicators)")
    print(f"  Records kept      : {len(cleaned)}")

    df = pd.DataFrame(cleaned)

    # Deduplicate — same indicator, source, country, year
    before = len(df)
    df = df.drop_duplicates(subset=["indicator_name", "source", "country", "year"])
    dupes = before - len(df)
    if dupes:
        print(f"  Duplicates removed: {dupes}")

    # Sort for readability
    df = df.sort_values(["indicator_name", "source", "year"]).reset_index(drop=True)

    return df


# ── Run Function ───────────────────────────────────────────
def run(world_bank_data: list[dict], imf_data: list[dict]) -> pd.DataFrame:
    """
    Takes raw data from all extractors, tags sources,
    applies unified schema, and returns a clean DataFrame.
    """
    print("\n── Tagging sources ───────────────────────────────")
    wb_tagged  = tag_source(world_bank_data,  source="world_bank")
    imf_tagged = tag_source(imf_data,         source="imf")

    all_raw = wb_tagged + imf_tagged
    print(f"  Total raw records : {len(all_raw)}")

    print("\n── Cleaning & normalising ────────────────────────")
    df = clean(all_raw)

    print(f"\n── Final dataset ─────────────────────────────────")
    print(f"  Shape             : {df.shape}")
    print(f"  Indicators        : {df['indicator_name'].nunique()}")
    print(f"  Year range        : {df['year'].min()} – {df['year'].max()}")
    print(f"  Sources           : {df['source'].unique().tolist()}")

    return df


# ── Entry Point ────────────────────────────────────────────
if __name__ == "__main__":
    # Import extractors and run them
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    from extractors.world_bank import run as wb_run
    from extractors.imf        import run as imf_run

    print("Extracting World Bank data...")
    wb_data  = wb_run()

    print("\nExtracting IMF data...")
    imf_data = imf_run()

    # Transform
    df = run(wb_data, imf_data)

    # Preview
    print("\n── Sample rows ───────────────────────────────────")
    print(df.head(10).to_string(index=False))

    print("\n── Indicators in dataset ─────────────────────────")
    print(df.groupby(["indicator_name", "source", "unit"])["year"].count().to_string())