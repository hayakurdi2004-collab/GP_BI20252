"""
wb_api.py — World Bank LPI Data Fetcher
Fetches live LPI data from the World Bank API (free, no key needed).
Falls back to local CSV if API is unavailable.
"""

import requests
import pandas as pd
import time

# ── Indicator codes ───────────────────────────────────────────
WB_INDICATORS = {
    "LP.LPI.OVRL.XQ": "LPI Overall Score",
    "LP.LPI.OVRL.RK": "LPI Overall Rank",
    "LP.LPI.CUST.XQ": "Customs Score",
    "LP.LPI.INFR.XQ": "Infrastructure Score",
    "LP.LPI.ITRN.XQ": "Int. Shipments Score",
    "LP.LPI.LOGS.XQ": "Logistics Quality Score",
    "LP.LPI.TRAC.XQ": "Tracking Score",
    "LP.LPI.TIME.XQ": "Timeliness Score",
}

WB_BASE = "https://api.worldbank.org/v2"


def fetch_indicator(indicator_code: str, country: str = "all",
                    per_page: int = 1000) -> pd.DataFrame:
    """
    Fetch a single indicator for all countries from World Bank API.
    Returns a DataFrame with columns: Country Code, Country Name, Year, Value.
    """
    url = (
        f"{WB_BASE}/country/{country}/indicator/{indicator_code}"
        f"?format=json&per_page={per_page}&mrv=20"
    )
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        if not data or len(data) < 2 or not data[1]:
            return pd.DataFrame()

        rows = []
        for item in data[1]:
            if item.get("value") is not None:
                rows.append({
                    "Country Code":   item["countryiso3code"],
                    "Country Name":   item["country"]["value"],
                    "Indicator Code": indicator_code,
                    "Indicator Short": WB_INDICATORS.get(indicator_code, indicator_code),
                    "Indicator Type": "Score" if indicator_code.endswith("XQ") else "Rank",
                    "Year":           int(item["date"]),
                    "Value":          float(item["value"]),
                })
        return pd.DataFrame(rows)

    except Exception as e:
        print(f"  ⚠️  API error for {indicator_code}: {e}")
        return pd.DataFrame()


def fetch_all_lpi(fallback_path: str = "data/LPI_clean.csv") -> pd.DataFrame:
    """
    Fetch all LPI indicators from World Bank API.
    If API fails, loads from local CSV fallback.

    Returns a clean DataFrame matching the structure of LPI_clean.csv.
    """
    print("🌐 Fetching LPI data from World Bank API...")
    all_frames = []

    for code, name in WB_INDICATORS.items():
        print(f"  → {name}...")
        df = fetch_indicator(code)
        if not df.empty:
            all_frames.append(df)
        time.sleep(0.3)   # be polite to the API

    if not all_frames:
        print("  ❌ API unavailable — loading from local CSV fallback")
        return pd.read_csv(fallback_path)

    combined = pd.concat(all_frames, ignore_index=True)

    # Add Region and Income Group from local CSV if available
    try:
        local = pd.read_csv(fallback_path)
        meta  = local[["Country Code", "Region", "Income Group"]].drop_duplicates()
        combined = combined.merge(meta, on="Country Code", how="left")
    except Exception:
        combined["Region"]       = "Unknown"
        combined["Income Group"] = "Unknown"

    print(f"  ✅ Fetched {len(combined)} records for "
          f"{combined['Country Name'].nunique()} countries")
    return combined


def fetch_jordan_latest(fallback_path: str = "data/LPI_clean.csv") -> dict:
    """
    Fetch Jordan's latest LPI scores directly from World Bank API.
    Returns a dict: {indicator_short: value}
    """
    print("🇯🇴 Fetching Jordan latest LPI from World Bank API...")
    result = {}

    for code, name in WB_INDICATORS.items():
        url = (
            f"{WB_BASE}/country/JOR/indicator/{code}"
            f"?format=json&mrv=1"
        )
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            if data and len(data) > 1 and data[1]:
                item = data[1][0]
                if item.get("value") is not None:
                    result[name] = {
                        "value": float(item["value"]),
                        "year":  int(item["date"]),
                    }
            time.sleep(0.2)
        except Exception as e:
            print(f"  ⚠️  Could not fetch {name}: {e}")

    if result:
        print(f"  ✅ Got {len(result)} indicators for Jordan")
    else:
        print("  ❌ API unavailable for Jordan data")

    return result


if __name__ == "__main__":
    # Quick test — run: python wb_api.py
    print("=" * 50)
    print("Testing World Bank LPI API")
    print("=" * 50)

    jordan = fetch_jordan_latest()
    if jordan:
        print("\nJordan Latest LPI:")
        for name, info in jordan.items():
            print(f"  {name:<30} {info['value']:.3f}  ({info['year']})")
    else:
        print("API not available — will use local CSV")