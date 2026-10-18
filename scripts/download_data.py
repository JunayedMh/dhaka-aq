"""
download_data.py
Downloads raw weather and hourly PM2.5 data from Open-Meteo for Dhaka.
Saves two CSV files to data/raw/.

Run from the project root:
    python download_data.py
"""

import os
import requests
import pandas as pd

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

DHAKA_LAT    = 23.81
DHAKA_LON    = 90.41
WINDOW_START = "2023-10-01"
WINDOW_END   = "2026-09-30"
RAW_DIR      = "data/raw"

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

os.makedirs(RAW_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Download 1: Daily weather
# ---------------------------------------------------------------------------

print("Downloading weather data...")

wx_resp = requests.get(
    "https://archive-api.open-meteo.com/v1/archive",
    params={
        "latitude":   DHAKA_LAT,
        "longitude":  DHAKA_LON,
        "start_date": WINDOW_START,
        "end_date":   WINDOW_END,
        "daily": ",".join([
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_sum",
            "wind_speed_10m_max",
            "wind_direction_10m_dominant",
            "relative_humidity_2m_max",
            "relative_humidity_2m_min",
            "sunshine_duration",
        ]),
        "timezone": "Asia/Dhaka",
    },
    timeout=30,
)
wx_resp.raise_for_status()

wx_daily = wx_resp.json()["daily"]
wx_df    = pd.DataFrame(wx_daily)

wx_path  = os.path.join(RAW_DIR, "weather_raw.csv")
wx_df.to_csv(wx_path, index=False)

print(f"  Saved: {wx_path}")
print(f"  Shape: {wx_df.shape}")
print(f"  Columns: {list(wx_df.columns)}")

# ---------------------------------------------------------------------------
# Download 2: Hourly PM2.5
# ---------------------------------------------------------------------------

print("\nDownloading PM2.5 data...")

aq_resp = requests.get(
    "https://air-quality-api.open-meteo.com/v1/air-quality",
    params={
        "latitude":   DHAKA_LAT,
        "longitude":  DHAKA_LON,
        "start_date": WINDOW_START,
        "end_date":   WINDOW_END,
        "hourly":     "pm2_5",
        "timezone":   "Asia/Dhaka",
    },
    timeout=60,
)
aq_resp.raise_for_status()

aq_hourly = aq_resp.json()["hourly"]
aq_df     = pd.DataFrame(aq_hourly)

aq_path   = os.path.join(RAW_DIR, "pm25_raw.csv")
aq_df.to_csv(aq_path, index=False)

print(f"  Saved: {aq_path}")
print(f"  Shape: {aq_df.shape}")
print(f"  Columns: {list(aq_df.columns)}")

# ---------------------------------------------------------------------------
# Sanity check
# ---------------------------------------------------------------------------

print("\n--- Sanity check ---")
print(f"  Weather rows : {len(wx_df)} (expected 1096)")
print(f"  PM2.5 rows   : {len(aq_df)} (expected 26304)")
print(f"  Weather nulls: {wx_df.isnull().sum().sum()}")
print(f"  PM2.5 nulls  : {aq_df.isnull().sum().sum()}")
print(f"\nWeather sample:")
print(wx_df.head(3).to_string(index=False))
print(f"\nPM2.5 sample:")
print(aq_df.head(5).to_string(index=False))

print("\nDone.")