# notebooks/clean_olympic_athletes.py
import re
import pandas as pd
from pathlib import Path

# --- paths ---
# replace ROOT so that any user can run this script directly
ROOT = Path(__file__).resolve().parent.parent  # .../olympic-prediction_2026
RAW   = ROOT / "data" / "raw"
CLEAN = ROOT / "data" / "clean"
CLEAN.mkdir(parents=True, exist_ok=True)

IN  = RAW / "olympic_athletes.json"
OUT = CLEAN / "olympic_athletes_clean.csv"


print("Input exists?", IN.exists(), "->", IN)

# fail early with a clear message
if not IN.exists():
    raise FileNotFoundError(f"Place olympic_athletes.json in {RAW} (checked: {IN})")

# robust JSON load: try normal, then fallback to lines=True
try:
    df = pd.read_json(IN)
except ValueError:
    try:
        df = pd.read_json(IN, lines=True)
    except Exception as e:
        raise SystemExit(f"Failed to read JSON {IN}: {e}")

print("Loaded:", df.shape)

# ensure expected columns exist (create with NA defaults if missing)
expected_cols = [
    "athlete_url","athlete_full_name","first_game","athlete_medals",
    "bio","athlete_year_birth","games_participations"
]
for c in expected_cols:
    if c not in df.columns:
        df[c] = pd.NA

# --- 1) Drop duplicates (safe subset intersection) ---
dup_subset = [c for c in ["athlete_url","athlete_full_name"] if c in df.columns]
if dup_subset:
    df = df.drop_duplicates(subset=dup_subset)

# --- 2) Extract first participation year from 'first_game' (safe) ---
df["first_year"] = pd.to_numeric(
    df["first_game"].astype(str).str.extract(r"(\d{4})")[0],
    errors="coerce"
)
# ...existing code...

# --- helper: parse medal text (return counts dict with ints, never None) ---
def parse_medal_text(x):
    """
    Parse various medal-text formats into a dict with integer counts:
      {"gold": 0, "silver": 0, "bronze": 0}
    Always returns a dict (counts may be 0).
    """
    if not isinstance(x, str) or not x.strip():
        return {"gold": 0, "silver": 0, "bronze": 0}
    s = x.strip()
    # normalize letters like G/S/B or words Gold/Silver/Bronze
    # accepts "2 Gold, 1 Silver", "3G 2S", "1 B" etc.
    medals = {"gold": 0, "silver": 0, "bronze": 0}
    # find pairs like "2 Gold" or "2G" or "2 G"
    for m in re.findall(r"(\d+)\s*(G|S|B|GOLD|SILVER|BRONZE|Gold|Silver|Bronze)", s, flags=re.IGNORECASE):
        count = int(m[0])
        typ = m[1].upper()
        if typ.startswith("G"):
            medals["gold"] += count
        elif typ.startswith("S"):
            medals["silver"] += count
        elif typ.startswith("B"):
            medals["bronze"] += count
    return medals

# --- 3) Clean 'athlete_medals' (use fillna to avoid errors) ---
# produce a consistent dict per row, then expand to numeric columns
medals_parsed = df["athlete_medals"].fillna("").astype(str).apply(parse_medal_text)
df["medal_gold"] = medals_parsed.apply(lambda d: d.get("gold", 0)).astype(int)
df["medal_silver"] = medals_parsed.apply(lambda d: d.get("silver", 0)).astype(int)
df["medal_bronze"] = medals_parsed.apply(lambda d: d.get("bronze", 0)).astype(int)
df["medal_total"] = df["medal_gold"] + df["medal_silver"] + df["medal_bronze"]

# keep a human-readable summary column too (no change to original data)
df["athlete_medals_clean"] = medals_parsed.apply(
    lambda d: ", ".join(f"{v} {k.capitalize()}" for k, v in d.items() if v > 0) or ""
)

# has_medal: numeric flag (0/1) derived from counts (robust)
df["has_medal"] = (df["medal_total"] > 0).astype(int)

# --- 4) Clean 'bio' ---
df["bio"] = df["bio"].fillna("").astype(str).str.strip()

# ...existing code...
# --- 5) Clean 'athlete_year_birth' ---
df["athlete_year_birth"] = pd.to_numeric(df["athlete_year_birth"], errors="coerce")
df.loc[df["athlete_year_birth"] < 1880, "athlete_year_birth"] = pd.NA

# --- 6) Handle missing small values (safe arithmetic with pandas) ---
df["first_year"] = df["first_year"].fillna(df["athlete_year_birth"] + 20)

# --- 7) Final tidy dataframe (reindex to avoid KeyError) ---
cols = [
    "athlete_full_name",
    "athlete_url",
    "athlete_year_birth",
    "games_participations",
    "first_game",
    "first_year",
    "athlete_medals_clean",
    "has_medal",
    "bio"
]
df_clean = df.reindex(columns=cols).copy()

# --- 8) Save ---
df_clean.to_csv(OUT, index=False, encoding="utf-8")
print(f" Saved cleaned athletes → {OUT}")
print(df_clean.info())
print(df_clean.head(5))
