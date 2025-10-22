# notebooks/clean_olympic_results.py
import ast
import re
import pandas as pd
from pathlib import Path

# -------- paths (portable) --------
ROOT  = Path(__file__).resolve().parents[1]
RAW   = ROOT / "data" / "raw"
CLEAN = ROOT / "data" / "clean"
CLEAN.mkdir(parents=True, exist_ok=True)

HTML_IN   = RAW / "olympic_results.html"
HOSTS_IN  = CLEAN / "olympic_hosts_clean.csv"  # join season if available
OUT_DETA  = CLEAN / "olympic_results_clean.csv"
OUT_AWARD = CLEAN / "olympic_results_awards.csv"

print(f"Input exists? {HTML_IN.exists()} -> {HTML_IN}")
if not HTML_IN.exists():
    raise FileNotFoundError(f"Place olympic_results.html in {RAW}")

# -------- load html table --------
# Use pandas to parse first table; fallback to manual BeautifulSoup if needed
try:
    df = pd.read_html(HTML_IN)[0]
except Exception:
    from bs4 import BeautifulSoup
    html = HTML_IN.read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(html, "html.parser")
    rows = []
    for tr in soup.select("table tr"):
        cells = [td.get_text(strip=True) for td in tr.find_all(["th","td"])]
        rows.append(cells)
    df = pd.DataFrame(rows[1:], columns=rows[0])

# -------- basic tidy --------
df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]
for junk in ["unnamed:_0", "index"]:
    if junk in df.columns:
        df = df.drop(columns=[junk])

# Normalize strings
for c in ["discipline_title","event_title","slug_game","participant_type","medal_type",
          "country_name","country_code","country_3_letter_code","athlete_url","athlete_full_name",
          "value_unit","value_type","rank_equal","rank_position"]:
    if c in df.columns:
        df[c] = df[c].astype(str).str.strip()

# Extract year
df["year"] = pd.to_numeric(df["slug_game"].str.extract(r"(\d{4})")[0], errors="coerce").astype("Int64")

# Standardize medal field, upper
if "medal_type" not in df.columns:
    df["medal_type"] = ""
df["medal_type"] = df["medal_type"].fillna("").str.upper()

# -------- expand 'athletes' (list of (name, url)) to rows --------
# Example value: "[('Name SURNAME','https://...'), ('Teammate','https://...')]"
def parse_athletes(cell):
    if pd.isna(cell) or not str(cell).strip():
        return []
    s = str(cell)
    # Fix common HTML export quirks
    s = s.replace("None", "''")
    try:
        val = ast.literal_eval(s)
        # Expect list of tuples (name, url) or list of strings
        out = []
        if isinstance(val, (list, tuple)):
            for it in val:
                if isinstance(it, (list, tuple)) and len(it) >= 1:
                    name = str(it[0]).strip()
                    url  = str(it[1]).strip() if len(it) >= 2 else ""
                    out.append((name, url))
                elif isinstance(it, str):
                    out.append((it.strip(), ""))
        return out
    except Exception:
        # fallback: split on '), (' heuristically
        names = re.findall(r"'([^']+)'", s)
        return [(n, "") for n in names]

# explode athletes into separate rows (keep original row if none)
df["_ath_list"] = df.get("athletes", "").apply(parse_athletes)
has_list = df["_ath_list"].apply(lambda x: len(x) > 0)

# Build exploded frame
exploded = df[has_list].explode("_ath_list").copy()
if not exploded.empty:
    exploded["athlete_full_name_from_list"] = exploded["_ath_list"].apply(lambda t: t[0] if isinstance(t, (list, tuple)) else "")
    exploded["athlete_url_from_list"]       = exploded["_ath_list"].apply(lambda t: t[1] if isinstance(t, (list, tuple)) and len(t) > 1 else "")

# Merge athlete columns: prefer explicit athlete_full_name if present; else from list
if not exploded.empty:
    exploded["athlete_full_name"] = exploded["athlete_full_name"].where(
        exploded["athlete_full_name"].astype(str).str.len() > 0,
        exploded["athlete_full_name_from_list"]
    )
    exploded["athlete_url"] = exploded["athlete_url"].where(
        exploded["athlete_url"].astype(str).str.len() > 0,
        exploded["athlete_url_from_list"]
    )

# Combine: rows without list + exploded rows
without_list = df[~has_list].copy()
df_expanded = pd.concat([without_list, exploded.drop(columns=["_ath_list","athlete_full_name_from_list","athlete_url_from_list"], errors="ignore")],
                        ignore_index=True)

# -------- create medal flags --------
for m in ["gold","silver","bronze"]:
    df_expanded[m] = 0
df_expanded.loc[df_expanded["medal_type"]=="GOLD","gold"] = 1
df_expanded.loc[df_expanded["medal_type"]=="SILVER","silver"] = 1
df_expanded.loc[df_expanded["medal_type"]=="BRONZE","bronze"] = 1

# Rank to numeric where possible
if "rank_position" in df_expanded.columns:
    df_expanded["rank_position_num"] = pd.to_numeric(df_expanded["rank_position"], errors="coerce").astype("Int64")

# Join season from hosts (optional)
if HOSTS_IN.exists():
    hosts = pd.read_csv(HOSTS_IN)
    season_map = dict(zip(hosts["year"], hosts["season"]))
    df_expanded["season"] = df_expanded["year"].map(season_map)

# Standard column order
keep_cols = [
    "year","season","slug_game",
    "discipline_title","event_title","participant_type",
    "medal_type","gold","silver","bronze",
    "rank_equal","rank_position","rank_position_num",
    "country_name","country_code","country_3_letter_code",
    "athlete_full_name","athlete_url",
    "value_type","value_unit"
]
keep_cols = [c for c in keep_cols if c in df_expanded.columns]
results_clean = df_expanded[keep_cols].copy().sort_values(["year","discipline_title","event_title","rank_position_num"], na_position="last")

# Save detailed results
results_clean.to_csv(OUT_DETA, index=False, encoding="utf-8")
print(f" saved detailed results -> {OUT_DETA}  (rows: {len(results_clean)})")

# -------- build awards table (1 row per medal award per NOC/event/year) --------
# Keep only rows with a medal; deduplicate by (year, sport, event, medal, NOC)
if not results_clean.empty and "country_3_letter_code" in results_clean.columns:
    awards = results_clean[results_clean["medal_type"].isin(["GOLD","SILVER","BRONZE"])].copy()
    # rename for consistency
    awards = awards.rename(columns={
        "discipline_title":"sport",
        "event_title":"event",
        "country_3_letter_code":"noc",
        "country_name":"country",
        "medal_type":"medal"
    })
    key = ["year","sport","event","medal","noc"]
    awards = awards.drop_duplicates(subset=[k for k in key if k in awards.columns]).copy()
    awards["award_count"] = 1
    # thin columns
    keep_aw = [c for c in ["year","season","sport","event","noc","country","medal","award_count"] if c in awards.columns]
    awards = awards[keep_aw].sort_values(["year","sport","event","noc","medal"])
    awards.to_csv(OUT_AWARD, index=False, encoding="utf-8")
    print(f" saved medal awards -> {OUT_AWARD}  (rows: {len(awards)})")
else:
    print(" skipped awards build (no medal rows or missing NOC column)")

# -------- quick sanity prints --------
print("\nNulls (results_clean):")
print(results_clean.isnull().sum().sort_values(ascending=False).head(12))

if HOSTS_IN.exists():
    fr = results_clean[results_clean["country_name"].str.upper()=="FRANCE"]
    print("\nFrance medal rows in results (sample):", len(fr[fr['gold']+fr['silver']+fr['bronze']>0]))
