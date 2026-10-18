"""
test-probe.py
Checks both Open-Meteo endpoints for Dhaka:
  - Historical weather archive (temperature, humidity, wind, rain)
  - Air quality archive (PM2.5 modelled)
Prints row counts, date range, and null counts for both.
"""

import requests
import pandas as pd

DHAKA_LAT    = 23.81
DHAKA_LON    = 90.41
WINDOW_START = "2023-10-01"
WINDOW_END   = "2026-09-30"

window_start_dt = pd.Timestamp(WINDOW_START)
window_end_dt   = pd.Timestamp(WINDOW_END)
total_days      = (window_end_dt - window_start_dt).days + 1

# ---------------------------------------------------------------------------
# Part 1: Weather archive
# ---------------------------------------------------------------------------

print("=" * 60)
print("PART 1 — Open-Meteo weather archive")
print("=" * 60)

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
            "relative_humidity_2m_max",
            "relative_humidity_2m_min",
        ]),
        "timezone": "Asia/Dhaka",
    },
    timeout=30,
)

wx_resp.raise_for_status()
wx_data = wx_resp.json()
daily   = wx_data.get("daily", {})
dates   = daily.get("time", [])

print(f"\n  Timezone returned : {wx_data.get('timezone')}")
print(f"  Rows returned     : {len(dates)}")
print(f"  Expected rows     : {total_days}")
print(f"  First date        : {dates[0] if dates else 'N/A'}")
print(f"  Last date         : {dates[-1] if dates else 'N/A'}")
print(f"  Row count match   : {len(dates) == total_days}")

print("\n  Nulls per variable:")
for var, values in daily.items():
    if var == "time":
        continue
    nulls = sum(1 for v in values if v is None)
    print(f"    {var:<40} {nulls} nulls / {len(values)} rows")

# ---------------------------------------------------------------------------
# Part 2: Air quality archive (PM2.5, full window)
# ---------------------------------------------------------------------------

print("\n" + "=" * 60)
print("PART 2 — Open-Meteo air quality archive (PM2.5)")
print("=" * 60)

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

if aq_resp.status_code != 200:
    print(f"\n  FAILED: {aq_resp.status_code}")
    print(f"  {aq_resp.text[:300]}")
else:
    aq_data   = aq_resp.json()
    hourly    = aq_data.get("hourly", {})
    aq_times  = hourly.get("time", [])
    aq_vals   = hourly.get("pm2_5", [])
    nulls     = sum(1 for v in aq_vals if v is None)

    expected_hours = total_days * 24

    print(f"\n  Timezone returned : {aq_data.get('timezone')}")
    print(f"  Rows returned     : {len(aq_times)}")
    print(f"  Expected rows     : {expected_hours} (hourly over {total_days} days)")
    print(f"  Row count match   : {len(aq_times) == expected_hours}")
    print(f"  Nulls             : {nulls} / {len(aq_vals)}")
    print(f"  Null %            : {100 * nulls / len(aq_vals):.1f}%")
    print(f"\n  First timestamp   : {aq_times[0] if aq_times else 'N/A'}")
    print(f"  Last timestamp    : {aq_times[-1] if aq_times else 'N/A'}")
    print(f"\n  Sample PM2.5 values (first 5 hours): {aq_vals[:5]}")
    print(f"  Sample PM2.5 values (last 5 hours) : {aq_vals[-5:]}")

print("\n" + "=" * 60)
print("Done.")
print("=" * 60)