# notebooks/clean_olympic_medals.py
import os, re
from pathlib import Path
import pandas as pd

# ---------- paths ----------
BASE  = Path(__file__).resolve().parent           # .../notebooks
ROOT  = BASE.parent                               # repo root
RAW   = ROOT / "data" / "raw"
CLEAN = ROOT / "data" / "clean"
CLEAN.mkdir(parents=True, exist_ok=True)

xlsx_path   = RAW / "olympic_medals.xlsx"
hosts_path  = CLEAN / "olympic_hosts.csv"  # created in previous step
out_clean   = CLEAN / "olympic_medals_clean.csv"
out_awards  = CLEAN / "olympic_medal_awards.csv"  # optional aggregated view

print("Excel path:", xlsx_path, "exists?", xlsx_path.exists())
if not xlsx_path.exists():
    raise FileNotFoundError(f"Place olympic_medals.xlsx in {RAW}")

# ---------- load medals ----------
df = pd.read_excel(xlsx_path, sheet_name=0)
print("Loaded rows:", len(df))

# 1) drop useless index column if present
for junk in ["Unnamed: 0", "unnamed: 0", "index"]:
    if junk in df.columns:
        df = df.drop(columns=[junk])

# 2) normalize column names
df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]

# 3) rename to a consistent schema
rename_map = {
    "discipline_title": "sport",
    "event_title": "event",
    "slug_game": "games_slug",
    "medal_type": "medal",
    "country_3_letter_code": "noc",
    "country_name": "country",
    "athlete_full_name": "athlete",
}
df = df.rename(columns={k:v for k,v in rename_map.items() if k in df.columns})

# 4) trim & uppercase where needed
for c in ["sport","event","event_gender","participant_type","participant_title","athlete","country","noc","games_slug","medal"]:
    if c in df.columns:
        df[c] = df[c].astype(str).str.strip()

if "noc" in df.columns:
    df["noc"] = df["noc"].str.upper()

# 5) extract year from games_slug (e.g., "tokyo-2020" -> 2020)
if "games_slug" in df.columns:
    df["year"] = pd.to_numeric(df["games_slug"].str.extract(r"(\d{4})")[0], errors="coerce").astype("Int64")

# 6) normalize medal values & create indicators
if "medal" in df.columns:
    df["medal"] = df["medal"].str.upper()
else:
    df["medal"] = ""

for m in ["gold","silver","bronze"]:
    df[m] = 0
df.loc[df["medal"]=="GOLD", "gold"] = 1
df.loc[df["medal"]=="SILVER", "silver"] = 1
df.loc[df["medal"]=="BRONZE", "bronze"] = 1

# 7) link season from hosts (if available)
season = None
if hosts_path.exists():
    hosts = pd.read_csv(hosts_path)
    # hosts has 'year' and 'season' from previous step
    season_map = dict(zip(hosts["year"], hosts["season"]))
    if "year" in df.columns:
        df["season"] = df["year"].map(season_map)
else:
    print(" Could not find hosts csv, skipping season join:", hosts_path)

# 8) select & order useful columns (keep what exists)
cols_wanted = [
    "year","season","games_slug",
    "sport","event","event_gender",
    "participant_type","participant_title",
    "athlete","athlete_url",
    "country","country_code","noc",
    "medal","gold","silver","bronze"
]
final_cols = [c for c in cols_wanted if c in df.columns]
df_clean = df[final_cols].copy()

# Optional: filter to only rows with an actual medal value
df_clean = df_clean[df_clean["medal"].isin(["GOLD","SILVER","BRONZE"])]

# 9) basic sanity fixes
# - Some team rows have athlete NaN; keep them (they represent a medal line), but set empty string for display
if "athlete" in df_clean.columns:
    df_clean["athlete"] = df_clean["athlete"].fillna("")

# - Ensure types
if "year" in df_clean.columns:
    df_clean["year"] = pd.to_numeric(df_clean["year"], errors="coerce").astype("Int64")

# 10) save normalized, row-per-medalist/team
df_clean.to_csv(out_clean, index=False, encoding="utf-8")
print(f" Saved normalized medalists/teams rows → {out_clean} ({len(df_clean)} rows)")

# ---------- OPTIONAL: build a deduplicated 'awards' table ----------
# One medal per (year, sport, event, medal, noc)
# This avoids counting multiple rows for the same team medal.
key_cols = [c for c in ["year","sport","event","medal","noc"] if c in df_clean.columns]
if len(key_cols) == 5:
    awards = (df_clean
              .drop_duplicates(subset=key_cols)
              .copy())

    # keep one representative row; add a 'award_count' column = 1
    awards["award_count"] = 1

    # reorder a compact set of columns
    keep_awards = [c for c in [
        "year","season","sport","event","event_gender","noc","country","medal","award_count"
    ] if c in awards.columns]
    awards = awards[keep_awards].sort_values(["year","sport","event","noc","medal"])
    awards.to_csv(out_awards, index=False, encoding="utf-8")
    print(f" Saved deduplicated medal awards → {out_awards} ({len(awards)} rows)")
else:
    print(" Skipped awards aggregation (missing one of: year, sport, event, medal, noc)")
