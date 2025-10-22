# notebooks/patch_medals_v2.py
import pandas as pd
from pathlib import Path
ROOT = Path("C:/Users/hasso/olympic-prediction_2026")

IN  = ROOT / "data" / "clean" / "olympic_medals_clean.csv"
OUT = ROOT / "data" / "clean" / "olympic_medals_clean_v2.csv"
OUT_AWARDS = ROOT / "data" / "clean" / "olympic_medal_awards_v2.csv"

print("Input exists?", IN.exists(), "->", IN)
med = pd.read_csv(IN)

# 1) Team vs Individual
med["is_team"] = (med["participant_type"].str.lower() == "gameteam").astype(int)

# 2) Backfill athlete for team rows: use participant_title, then fallback "Country Team"
is_team = med["is_team"] == 1
missing_ath = med["athlete"].isna() | (med["athlete"].astype(str).str.strip() == "")
med.loc[is_team & missing_ath, "athlete"] = med.loc[is_team & missing_ath, "participant_title"].fillna("").replace("", pd.NA)

still_missing = med["athlete"].isna() | (med["athlete"].astype(str).str.strip() == "")
med.loc[is_team & still_missing, "athlete"] = (med.loc[is_team & still_missing, "country"].astype(str).str.strip() + " Team").str.strip()

# 3) Normalize empties
for col in ["athlete", "participant_title"]:
    med[col] = med[col].fillna("").astype(str).str.strip()

# 4) Rebuild ISO2 country_code where missing (uses pycountry + overrides)
try:
    import pycountry
    overrides = {
        "Great Britain": "GB", "United Kingdom": "GB",
        "United States of America": "US", "Russia": "RU",
        "Russian Federation": "RU", "Republic of Korea": "KR",
        "South Korea": "KR", "Democratic People's Republic of Korea": "KP",
        "North Korea": "KP", "Côte d'Ivoire": "CI", "Ivory Coast": "CI",
        "Hong Kong, China": "HK", "People's Republic of China": "CN",
        "China": "CN", "Chinese Taipei": "TW", "Iran, Islamic Republic of": "IR",
        "Viet Nam": "VN", "Lao People's Democratic Republic": "LA",
        "Syrian Arab Republic": "SY", "Bolivia (Plurinational State of)": "BO",
        "Congo, Democratic Republic of the": "CD", "Congo": "CG",
        "Tanzania, United Republic of": "TZ", "Moldova, Republic of": "MD",
        "Palestine": "PS",
    }
    def to_iso2(country):
        if not isinstance(country, str) or not country.strip():
            return None
        name = country.strip()
        if name in overrides:
            return overrides[name]
        try:
            return pycountry.countries.lookup(name).alpha_2
        except Exception:
            return None

    missing_iso2 = med["country_code"].isna() | (med["country_code"].astype(str).str.strip()=="")
    med.loc[missing_iso2, "country_code"] = med.loc[missing_iso2, "country"].map(to_iso2)
except Exception as e:
    print(" Skipping ISO rebuild (install pycountry if needed). Error:", e)

# 5) Ensure medal flags consistent
valid = ["GOLD","SILVER","BRONZE"]
med = med[med["medal"].isin(valid)].copy()
for mcol, val in [("gold","GOLD"), ("silver","SILVER"), ("bronze","BRONZE")]:
    med[mcol] = (med["medal"] == val).astype(int)

# 6) Save v2 (does NOT overwrite v1)
med.to_csv(OUT, index=False, encoding="utf-8")
print(f" Saved v2 -> {OUT}  (rows: {len(med)})")

# 7) Optional: deduplicated awards (one medal per (year,sport,event,medal,noc))
key = [c for c in ["year","sport","event","medal","noc"] if c in med.columns]
if len(key) == 5:
    awards = med.drop_duplicates(subset=key).copy()
    awards["award_count"] = 1
    keep = [c for c in ["year","season","sport","event","event_gender","noc","country","medal","award_count"] if c in awards.columns]
    awards = awards[keep].sort_values(["year","sport","event","noc","medal"])
    awards.to_csv(OUT_AWARDS, index=False, encoding="utf-8")
    print(f" Saved awards v2 -> {OUT_AWARDS}  (rows: {len(awards)})")
else:
    print(" Skipped awards v2 (missing one of: year, sport, event, medal, noc)")

# 8) Nulls report
print("\nNulls after patch v2:")
print(med.isnull().sum())
