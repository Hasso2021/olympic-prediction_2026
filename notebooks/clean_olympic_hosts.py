# notebooks/clean_olympic_hosts.py
import os, re
from pathlib import Path
import pandas as pd

# --- Resolve folders relative to this script ---
BASE = Path(__file__).resolve().parent          # .../olympic-prediction_2026/notebooks
RAW  = BASE.parent / "data" / "raw"             # .../data/raw
CLEAN= BASE.parent / "data" / "clean"           # .../data/clean
CLEAN.mkdir(parents=True, exist_ok=True)

xml_path = RAW / "olympic_hosts.xml"
print("XML absolute path:", xml_path)
print("Exists?", xml_path.exists())

if not xml_path.exists():
    raise FileNotFoundError(f"Could not find file at: {xml_path}\n"
                            "→ Check your folder structure or move olympic_hosts.xml into data/raw/")

# --- Robust XML load (from file path) ---
# If you previously saw a FutureWarning, it was because pandas thought
# you passed raw XML text. Passing a proper file path avoids that.
df_host = pd.read_xml(xml_path)  # requires lxml installed
print("Loaded rows:", len(df_host))

# --- Preprocess / tidy ---
# your columns are: index, game_slug, game_end_date, game_start_date, game_location,
#                   game_name, game_season, game_year

# Drop the useless 'index'
if "index" in df_host.columns:
    df_host = df_host.drop(columns=["index"])

# Parse dates to datetime (UTC) and compute duration in days
for c in ["game_start_date", "game_end_date"]:
    df_host[c] = pd.to_datetime(df_host[c], errors="coerce", utc=True)

df_host["duration_days"] = (df_host["game_end_date"] - df_host["game_start_date"]).dt.days

# Extract city from "game_name" (e.g., "Beijing 2022" -> "Beijing")
def extract_city(name: str):
    if pd.isna(name): 
        return None
    m = re.match(r"^(.*?)(?:\s+\d{4})$", str(name).strip())
    return m.group(1).strip() if m else str(name).strip()

df_host["city"] = df_host["game_name"].apply(extract_city)

# Normalize season
df_host["game_season"] = df_host["game_season"].astype(str).str.capitalize()

# Standardize country names from game_location (extend as needed)
country_map = {
    "Great Britain": "United Kingdom",
    "United States of America": "United States",
    "Russian Federation": "Russia",
    "Republic of Korea": "South Korea",
    "People's Republic of China": "China",
}
df_host["country"] = df_host["game_location"].replace(country_map)

# Final tidy schema
hosts_tidy = (
    df_host.rename(columns={
        "game_slug": "slug",
        "game_year": "year",
        "game_season": "season",
        "game_start_date": "start_date",
        "game_end_date": "end_date",
        "game_name": "name",
    })
    [["year", "season", "city", "country", "slug", "name", "start_date", "end_date", "duration_days"]]
    .sort_values(["year", "season"])
    .reset_index(drop=True)
)

# Save
out_path = CLEAN / "olympic_hosts_clean.csv"
hosts_tidy.to_csv(out_path, index=False, encoding="utf-8")
print(f"✅ Saved {len(hosts_tidy)} rows → {out_path}")
