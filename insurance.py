import io
import os
import re
import sqlite3
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

import pandas as pd
import requests
import streamlit as st

# ============================================================
# CONFIG
# ============================================================

DEFAULT_COMPANIES = {
    # Big 3 insurers (by enrollment; also among largest by market cap)
    "UnitedHealth Group": "UNH",
    "Elevance Health": "ELV",
    "CVS Health (Aetna)": "CVS",
    # Big 3 drug wholesalers
    "McKesson": "MCK",
    "Cencora": "COR",
    "Cardinal Health": "CAH",
}

# 13F infotable uses CUSIP (9 chars). This avoids Yahoo entirely.
# Sources:
# - UNH 91324P102 (StockAnalysis/QuantumOnline)
# - ELV 036752103 (StockAnalysis)
# - CVS 126650100 (SEC filing/StockAnalysis)
# - MCK 58155Q103 (StockAnalysis/SEC filing)
# - COR 03073E105 (SEC filing - legacy AmerisourceBergen; still common-stock CUSIP widely used)
# - CAH 14149Y108 (Cardinal Health IR/StockAnalysis)
TICKER_TO_CUSIP = {
    "UNH": "91324P102",
    "ELV": "036752103",
    "CVS": "126650100",
    "MCK": "58155Q103",
    "COR": "03073E105",
    "CAH": "14149Y108",
}

DEFAULT_TAG_RULES = [
    ("Vanguard", r"\bVanguard\b"),
    ("BlackRock", r"\bBlackRock\b|\bBlackrock\b"),
    ("State Street", r"\bState Street\b"),
    ("CalPERS", r"\bCalifornia Public Employees' Retirement System\b|\bCalPERS\b"),
    ("CalSTRS", r"\bCalifornia State Teachers' Retirement System\b|\bCalSTRS\b"),
    ("NY State Common RF", r"\bNew York State Common Retirement Fund\b"),
    ("Florida SBA", r"\bFlorida State Board of Administration\b|\bFlorida SBA\b"),
    ("Pension/Retirement (Generic)", r"\bRetirement\b|\bPension\b"),
    ("Index Fund/ETF (Generic)", r"\bIndex\b|\bETF\b"),
]

DB_PATH_DEFAULT = "ownership_13f.sqlite"

SEC_13F_DATASETS_PAGE = "https://www.sec.gov/data-research/sec-markets-data/form-13f-data-sets"
SEC_DOWNLOAD_DIR = "sec_cache"  # local cache directory for zips

# ============================================================
# DATA MODEL
# ============================================================

@dataclass
class IngestMeta:
    asof_utc: str
    quarter_label: str
    zip_url: str
    ingest_ok: int
    error: Optional[str] = None


# ============================================================
# DB HELPERS
# ============================================================

def db_connect(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn


def db_init(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS quarter_meta (
            quarter_id INTEGER PRIMARY KEY AUTOINCREMENT,
            quarter_label TEXT NOT NULL,
            quarter_end TEXT,
            zip_url TEXT NOT NULL,
            asof_utc TEXT NOT NULL,
            ingest_ok INTEGER NOT NULL,
            error TEXT
        );

        CREATE UNIQUE INDEX IF NOT EXISTS uq_quarter_meta_label
        ON quarter_meta(quarter_label);

        -- Canonical holdings derived from 13F infotable + coverpage/submission joins
        CREATE TABLE IF NOT EXISTS holdings_13f (
            holding_id INTEGER PRIMARY KEY AUTOINCREMENT,
            quarter_end TEXT NOT NULL,
            quarter_label TEXT NOT NULL,
            ticker TEXT NOT NULL,
            cusip TEXT NOT NULL,
            manager_cik TEXT,
            manager_name TEXT NOT NULL,
            shares REAL,
            value_usd REAL
        );

        CREATE INDEX IF NOT EXISTS idx_holdings_qtr_ticker
        ON holdings_13f(quarter_end, ticker);

        CREATE INDEX IF NOT EXISTS idx_holdings_qtr_manager
        ON holdings_13f(quarter_end, manager_name);

        -- Optional: keep a mapping of accession -> manager/period (debug/traceability)
        CREATE TABLE IF NOT EXISTS accession_map (
            accession_number TEXT PRIMARY KEY,
            period_of_report TEXT,
            manager_cik TEXT,
            manager_name TEXT
        );
        """
    )
    conn.commit()


# ============================================================
# UTILS
# ============================================================

def apply_tags(holder_name: str, custom_rules: List[Tuple[str, str]]) -> List[str]:
    tags: List[str] = []
    if not holder_name:
        return tags
    for tag, pattern in custom_rules:
        if re.search(pattern, holder_name, flags=re.IGNORECASE):
            tags.append(tag)
    return tags


def sec_headers(app_name: str, email: str) -> Dict[str, str]:
    """
    SEC asks automated clients to identify themselves with a real contact.
    Put your real email in the sidebar input.
    """
    ua = f"{app_name} ({email})" if email else app_name
    return {
        "User-Agent": ua,
        "Accept-Encoding": "gzip, deflate, br",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Connection": "keep-alive",
    }


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def parse_sec_dataset_links(html: str) -> List[Tuple[str, str]]:
    """
    Returns list of (label, zip_url).
    """
    # The SEC page contains anchors whose href ends with _form13f.zip
    # Example: https://www.sec.gov/files/structureddata/data/form-13f-data-sets/01jun2025-31aug2025_form13f.zip
    zip_urls = sorted(set(re.findall(r"https://www\.sec\.gov/files/structureddata/data/form-13f-data-sets/[^\"']+_form13f\.zip", html)))
    pairs: List[Tuple[str, str]] = []
    for u in zip_urls:
        fname = u.rsplit("/", 1)[-1]
        label = fname.replace("_form13f.zip", "").replace("-", " - ")
        pairs.append((label, u))
    # Newest tend to appear last alphabetically, but not guaranteed; we’ll keep list and also store label.
    return pairs


def quarter_end_from_label(label: str) -> Optional[str]:
    """
    Best-effort derive quarter_end from filename label like:
      '01jun2025 - 31aug2025'  -> 2025-08-31
      '01sep2025 - 30nov2025'  -> 2025-11-30
    """
    m = re.search(r"(\d{2}[a-z]{3}\d{4})\s*-\s*(\d{2}[a-z]{3}\d{4})", label, flags=re.IGNORECASE)
    if not m:
        return None
    end_s = m.group(2)
    # Parse ddmonyyyy to YYYY-MM-DD
    try:
        dt = datetime.strptime(end_s, "%d%b%Y").date()
        return dt.isoformat()
    except Exception:
        return None


# ============================================================
# SEC: LIST AVAILABLE QUARTERS
# ============================================================

@st.cache_data(show_spinner=False, ttl=6 * 60 * 60)
def fetch_available_quarters(app_name: str, email: str) -> List[Tuple[str, str, Optional[str]]]:
    """
    Returns list of (quarter_label, zip_url, quarter_end_iso)
    """
    r = requests.get(SEC_13F_DATASETS_PAGE, headers=sec_headers(app_name, email), timeout=60)
    r.raise_for_status()
    pairs = parse_sec_dataset_links(r.text)
    out = []
    for label, url in pairs:
        out.append((label, url, quarter_end_from_label(label)))
    # Prefer newest first by quarter_end if present
    out.sort(key=lambda x: (x[2] or ""), reverse=True)
    return out


# ============================================================
# SEC: DOWNLOAD + INGEST 13F ZIP
# ============================================================

def _zip_cache_path(quarter_label: str) -> str:
    safe = re.sub(r"[^a-zA-Z0-9_\-\.]+", "_", quarter_label)
    return os.path.join(SEC_DOWNLOAD_DIR, f"{safe}.zip")


def download_zip_if_needed(zip_url: str, quarter_label: str, app_name: str, email: str) -> str:
    """
    Returns local path to zip (cached on disk).
    """
    ensure_dir(SEC_DOWNLOAD_DIR)
    path = _zip_cache_path(quarter_label)
    if os.path.exists(path) and os.path.getsize(path) > 1_000_000:
        return path

    with requests.get(zip_url, headers=sec_headers(app_name, email), stream=True, timeout=300) as r:
        r.raise_for_status()
        with open(path, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)
    return path


def _find_member(z: zipfile.ZipFile, table_prefix: str) -> Optional[str]:
    """
    Finds member like 'INFOTABLE.tsv' or 'COVERPAGE.tsv' regardless of case or folder.
    """
    names = z.namelist()
    # SEC doc says: SUBMISSION, COVERPAGE, INFOTABLE etc. TSV, tab-delimited UTF-8
    for n in names:
        base = n.rsplit("/", 1)[-1]
        if base.upper().startswith(table_prefix.upper()) and base.lower().endswith(".tsv"):
            return n
    return None


def ingest_13f_quarter(
    conn: sqlite3.Connection,
    quarter_label: str,
    quarter_end: Optional[str],
    zip_url: str,
    tickers: List[str],
    app_name: str,
    email: str,
) -> IngestMeta:
    """
    Ingests SEC 13F dataset ZIP into holdings_13f table for specified tickers.
    Uses:
      SUBMISSION.tsv: accession_number, cik, periodofreport
      COVERPAGE.tsv: accession_number, filingmanager_name
      INFOTABLE.tsv: accession_number, cusip, sshprnamt, value
    """
    asof = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    cusips = {TICKER_TO_CUSIP[t] for t in tickers if t in TICKER_TO_CUSIP}

    try:
        local_zip = download_zip_if_needed(zip_url, quarter_label, app_name, email)

        with zipfile.ZipFile(local_zip, "r") as z:
            sub_m = _find_member(z, "SUBMISSION")
            cov_m = _find_member(z, "COVERPAGE")
            info_m = _find_member(z, "INFOTABLE")

            if not (sub_m and cov_m and info_m):
                missing = [k for k, v in [("SUBMISSION", sub_m), ("COVERPAGE", cov_m), ("INFOTABLE", info_m)] if not v]
                raise RuntimeError(f"Missing TSV(s) in ZIP: {missing}")

            # ---- Read SUBMISSION (accession -> cik, period)
            with z.open(sub_m) as fsub:
                sub = pd.read_csv(
                    fsub,
                    sep="\t",
                    dtype=str,
                    usecols=["ACCESSION_NUMBER", "CIK", "PERIODOFREPORT"],
                    low_memory=False,
                )
            sub.columns = [c.strip().upper() for c in sub.columns]
            sub = sub.rename(columns={"ACCESSION_NUMBER": "accession_number", "CIK": "manager_cik", "PERIODOFREPORT": "period_of_report"})

            # Normalize period format if it’s DD-MON-YYYY
            def _norm_period(x: str) -> str:
                if not isinstance(x, str) or not x:
                    return ""
                x = x.strip()
                for fmt in ("%d-%b-%Y", "%Y-%m-%d"):
                    try:
                        return datetime.strptime(x, fmt).date().isoformat()
                    except Exception:
                        pass
                return x  # keep raw

            sub["period_of_report"] = sub["period_of_report"].apply(_norm_period)

            # ---- Read COVERPAGE (accession -> manager_name)
            with z.open(cov_m) as fcov:
                cov = pd.read_csv(
                    fcov,
                    sep="\t",
                    dtype=str,
                    usecols=["ACCESSION_NUMBER", "FILINGMANAGER_NAME"],
                    low_memory=False,
                )
            cov.columns = [c.strip().upper() for c in cov.columns]
            cov = cov.rename(columns={"ACCESSION_NUMBER": "accession_number", "FILINGMANAGER_NAME": "manager_name"})

            # ---- Join accession map (for manager selector + auditing)
            acc = sub.merge(cov, on="accession_number", how="inner")
            acc["manager_name"] = acc["manager_name"].fillna("").str.strip()
            acc = acc[acc["manager_name"] != ""].copy()

            # Quarter end: if not provided, infer from the dominant period_of_report
            inferred_qend = quarter_end
            if not inferred_qend:
                # most common period in this dataset
                mode = acc["period_of_report"].mode()
                inferred_qend = mode.iloc[0] if len(mode) else None

            if not inferred_qend:
                inferred_qend = "UNKNOWN"

            # Persist accession map (upsert)
            cur = conn.cursor()
            for _, r in acc.iterrows():
                cur.execute(
                    """
                    INSERT OR REPLACE INTO accession_map(accession_number, period_of_report, manager_cik, manager_name)
                    VALUES (?, ?, ?, ?)
                    """,
                    (r["accession_number"], r["period_of_report"], r.get("manager_cik"), r["manager_name"]),
                )
            conn.commit()

            # ---- Stream INFOTABLE and filter by CUSIP in chunks
            # VALUE is market value in thousands of dollars per SEC doc.
            chunks = []
            with z.open(info_m) as finfo:
                it = pd.read_csv(
                    finfo,
                    sep="\t",
                    dtype=str,
                    usecols=["ACCESSION_NUMBER", "CUSIP", "VALUE", "SSHPRNAMT"],
                    chunksize=250_000,
                    low_memory=False,
                )
                for chunk in it:
                    chunk.columns = [c.strip().upper() for c in chunk.columns]
                    chunk = chunk.rename(
                        columns={
                            "ACCESSION_NUMBER": "accession_number",
                            "CUSIP": "cusip",
                            "VALUE": "value_k",
                            "SSHPRNAMT": "shares",
                        }
                    )
                    chunk["cusip"] = chunk["cusip"].astype(str).str.strip()
                    chunk = chunk[chunk["cusip"].isin(cusips)].copy()
                    if chunk.empty:
                        continue
                    # numeric coercion
                    chunk["value_usd"] = pd.to_numeric(chunk["value_k"], errors="coerce") * 1000.0
                    chunk["shares"] = pd.to_numeric(chunk["shares"], errors="coerce")
                    chunks.append(chunk[["accession_number", "cusip", "shares", "value_usd"]])

            if not chunks:
                raise RuntimeError("No matching CUSIP rows found in INFOTABLE for selected tickers.")

            info = pd.concat(chunks, ignore_index=True)
            # join manager identity
            info = info.merge(acc[["accession_number", "manager_cik", "manager_name"]], on="accession_number", how="left")
            info = info[info["manager_name"].notna()].copy()

            # Map cusip -> ticker
            cusip_to_ticker = {v: k for k, v in TICKER_TO_CUSIP.items()}
            info["ticker"] = info["cusip"].map(cusip_to_ticker)

            # Aggregate by quarter_end + ticker + manager
            agg = (
                info.groupby(["ticker", "cusip", "manager_cik", "manager_name"], dropna=False)[["shares", "value_usd"]]
                .sum()
                .reset_index()
            )
            agg["quarter_end"] = inferred_qend
            agg["quarter_label"] = quarter_label

            # Delete prior ingests for this quarter_label to make it idempotent
            conn.execute("DELETE FROM holdings_13f WHERE quarter_label = ?", (quarter_label,))
            conn.commit()

            # Insert
            agg.to_sql("holdings_13f", conn, if_exists="append", index=False)

            # Record quarter_meta
            conn.execute(
                """
                INSERT OR REPLACE INTO quarter_meta(quarter_label, quarter_end, zip_url, asof_utc, ingest_ok, error)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (quarter_label, inferred_qend, zip_url, asof, 1, None),
            )
            conn.commit()

        return IngestMeta(asof, quarter_label, zip_url, 1, None)

    except Exception as e:
        conn.execute(
            """
            INSERT OR REPLACE INTO quarter_meta(quarter_label, quarter_end, zip_url, asof_utc, ingest_ok, error)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (quarter_label, quarter_end, zip_url, asof, 0, str(e)),
        )
        conn.commit()
        return IngestMeta(asof, quarter_label, zip_url, 0, str(e))


# ============================================================
# QUERY HELPERS (Quarter selector / Manager selector / Changes)
# ============================================================

def list_loaded_quarters(conn: sqlite3.Connection) -> pd.DataFrame:
    return pd.read_sql_query(
        """
        SELECT quarter_label, quarter_end, zip_url, asof_utc, ingest_ok, error
        FROM quarter_meta
        ORDER BY quarter_end DESC
        """,
        conn,
    )


def get_holdings_for_quarter(conn: sqlite3.Connection, quarter_end: str, tickers: List[str]) -> pd.DataFrame:
    q = f"""
    SELECT quarter_end, quarter_label, ticker, cusip, manager_cik, manager_name, shares, value_usd
    FROM holdings_13f
    WHERE quarter_end = ?
      AND ticker IN ({",".join(["?"] * len(tickers))})
    """
    return pd.read_sql_query(q, conn, params=[quarter_end] + tickers)


def get_prior_quarter_end(conn: sqlite3.Connection, quarter_end: str) -> Optional[str]:
    df = pd.read_sql_query(
        """
        SELECT DISTINCT quarter_end
        FROM holdings_13f
        WHERE quarter_end < ?
        ORDER BY quarter_end DESC
        LIMIT 1
        """,
        conn,
        params=[quarter_end],
    )
    if df.empty:
        return None
    return str(df["quarter_end"].iloc[0])


def compute_changes_since_prior(conn: sqlite3.Connection, quarter_end: str, tickers: List[str]) -> Tuple[pd.DataFrame, Optional[str]]:
    prior = get_prior_quarter_end(conn, quarter_end)
    cur = get_holdings_for_quarter(conn, quarter_end, tickers)
    if not prior:
        cur["shares_change"] = None
        cur["value_change"] = None
        return cur, None

    prev = get_holdings_for_quarter(conn, prior, tickers)
    key = ["ticker", "cusip", "manager_cik", "manager_name"]
    cur2 = cur.merge(prev[key + ["shares", "value_usd"]], on=key, how="left", suffixes=("", "_prev"))
    cur2["shares_change"] = cur2["shares"] - cur2["shares_prev"]
    cur2["value_change"] = cur2["value_usd"] - cur2["value_usd_prev"]
    return cur2, prior


# ============================================================
# STREAMLIT UI
# ============================================================

st.set_page_config(page_title="SEC 13F Ownership Tracker", layout="wide")
st.title("Institutional Ownership Tracker — SEC 13F (No Yahoo)")
st.caption(
    "Computes largest institutional holders from SEC Form 13F datasets (quarterly). "
    "This avoids Yahoo entirely and keeps a historical DB for trends + changes."
)

# Sidebar controls
st.sidebar.header("Controls")

db_path = st.sidebar.text_input("SQLite DB Path", DB_PATH_DEFAULT)
conn = db_connect(db_path)
db_init(conn)

st.sidebar.subheader("SEC Identification (required for reliable access)")
app_name = st.sidebar.text_input("App name (User-Agent)", "FollowTheHealthInsuranceMoney")
contact_email = st.sidebar.text_input("Contact email (User-Agent)", "")

st.sidebar.subheader("Company Universe")
selected_names = st.sidebar.multiselect(
    "Track these companies",
    options=list(DEFAULT_COMPANIES.keys()),
    default=list(DEFAULT_COMPANIES.keys()),
)
selected_tickers = [DEFAULT_COMPANIES[n] for n in selected_names]

st.sidebar.subheader("Investor Tag Rules")
tag_rules = DEFAULT_TAG_RULES.copy()
if st.sidebar.toggle("Add a custom tag rule"):
    new_tag = st.sidebar.text_input("Tag name", "")
    new_pat = st.sidebar.text_input("Regex pattern (case-insensitive)", "")
    if new_tag and new_pat:
        tag_rules.append((new_tag, new_pat))

# Fetch quarter list from SEC
with st.sidebar.expander("Available SEC 13F quarters", expanded=False):
    try:
        avail = fetch_available_quarters(app_name, contact_email)
        st.write(f"Found {len(avail)} downloadable datasets.")
    except Exception as e:
        avail = []
        st.error(f"Could not fetch SEC datasets list: {e}")

# Ingest controls
st.sidebar.subheader("Ingestion")
if avail:
    avail_labels = [a[0] for a in avail]
    default_label = avail_labels[0]
    ingest_label = st.sidebar.selectbox("Choose dataset to ingest", options=avail_labels, index=0)
    ingest_row = next((a for a in avail if a[0] == ingest_label), None)
else:
    ingest_label, ingest_row = None, None

ingest_btn = st.sidebar.button("Ingest selected quarter")

if ingest_btn:
    if not ingest_row:
        st.sidebar.error("No dataset selected / available.")
    else:
        q_label, q_url, q_end = ingest_row
        with st.spinner("Downloading + ingesting SEC 13F dataset (this can take a few minutes)…"):
            meta = ingest_13f_quarter(
                conn=conn,
                quarter_label=q_label,
                quarter_end=q_end,
                zip_url=q_url,
                tickers=selected_tickers,
                app_name=app_name,
                email=contact_email,
            )
        if meta.ingest_ok:
            st.sidebar.success(f"Ingested: {q_label}")
        else:
            st.sidebar.error(f"Ingest failed: {meta.error}")

# Tabs
tab_overview, tab_company, tab_manager, tab_data, tab_debug = st.tabs(
    ["Overview", "Company Detail", "Manager View", "Data / Exports", "Debug"]
)

# -----------------------------
# Quarter selector (global)
# -----------------------------
loaded = list_loaded_quarters(conn)
loaded_ok = loaded[(loaded["ingest_ok"] == 1) & (loaded["quarter_end"].notna())].copy()

if loaded_ok.empty:
    st.info("No ingested SEC 13F data yet. Use the sidebar to ingest the latest quarter dataset.")
    st.stop()

# Quarter selector
quarter_options = loaded_ok.sort_values("quarter_end", ascending=False)["quarter_end"].tolist()
quarter_end = st.sidebar.selectbox("Quarter Selector (quarter_end)", options=quarter_options, index=0)

# Pull holdings for current quarter + compute changes since prior
holdings_cur, prior_q = compute_changes_since_prior(conn, quarter_end, selected_tickers)

# Manager selector options based on current quarter + selected universe
manager_list = sorted(holdings_cur["manager_name"].dropna().unique().tolist())
manager_choice = st.sidebar.selectbox("Manager Selector", options=["All managers"] + manager_list, index=0)

if manager_choice != "All managers":
    holdings_view = holdings_cur[holdings_cur["manager_name"] == manager_choice].copy()
else:
    holdings_view = holdings_cur.copy()

# Add tags + helpful display fields
holdings_view["tags"] = holdings_view["manager_name"].apply(lambda x: ", ".join(apply_tags(str(x), tag_rules)))
holdings_view["value_usd_m"] = (holdings_view["value_usd"] / 1_000_000.0).round(2)
if "value_change" in holdings_view.columns:
    holdings_view["value_change_m"] = (holdings_view["value_change"] / 1_000_000.0).round(2)


# -----------------------------
# Overview tab
# -----------------------------
with tab_overview:
    st.subheader("Top institutional holders (SEC 13F)")

    if prior_q:
        st.caption(f"Quarter: **{quarter_end}** (changes vs prior quarter **{prior_q}**).")
    else:
        st.caption(f"Quarter: **{quarter_end}** (no prior quarter loaded to compute changes).")

    # Top holders per company by value
    topn = st.slider("Top N managers per company", 5, 50, 15, 5)

    view = holdings_view.copy()
    view = view.sort_values(["ticker", "value_usd"], ascending=[True, False])
    view_ranked = view.groupby("ticker").head(topn)

    st.markdown("### Top holders by company (value)")
    st.dataframe(
        view_ranked[
            [
                "ticker",
                "manager_name",
                "tags",
                "shares",
                "value_usd_m",
                "shares_change",
                "value_change_m",
            ]
        ],
        width="stretch",
        hide_index=True,
    )

    st.markdown("### Big 3 concentration (by manager name tags)")
    big3 = view[view["tags"].str.contains("Vanguard|BlackRock|State Street", regex=True, na=False)].copy()
    if big3.empty:
        st.caption("No Big 3 managers matched via tag rules in the current filtered view.")
    else:
        conc = big3.groupby("ticker")[["value_usd"]].sum().reset_index()
        conc["big3_value_usd_m"] = (conc["value_usd"] / 1_000_000.0).round(2)
        st.dataframe(conc[["ticker", "big3_value_usd_m"]], width="stretch", hide_index=True)

    st.markdown("### Concentration chart (Top holders value, per company)")
    chart_df = view_ranked.pivot_table(index="manager_name", columns="ticker", values="value_usd_m", aggfunc="sum").fillna(0)
    st.bar_chart(chart_df, width="stretch")


# -----------------------------
# Company detail tab
# -----------------------------
with tab_company:
    st.subheader("Company Detail — trends across quarters")

    ticker = st.selectbox("Choose a company", options=selected_tickers, index=0)
    company_cur = holdings_cur[holdings_cur["ticker"] == ticker].copy()
    company_cur["tags"] = company_cur["manager_name"].apply(lambda x: ", ".join(apply_tags(str(x), tag_rules)))
    company_cur["value_usd_m"] = (company_cur["value_usd"] / 1_000_000.0).round(2)
    if "value_change" in company_cur.columns:
        company_cur["value_change_m"] = (company_cur["value_change"] / 1_000_000.0).round(2)

    st.markdown("### Current quarter top holders (by value)")
    company_top = company_cur.sort_values("value_usd", ascending=False).head(30)
    st.dataframe(
        company_top[["manager_name", "tags", "shares", "value_usd_m", "shares_change", "value_change_m"]],
        width="stretch",
        hide_index=True,
    )

    st.markdown("### Trend (value) for selected managers across loaded quarters")
    # Build history for this ticker across all quarters loaded
    hist = pd.read_sql_query(
        """
        SELECT quarter_end, ticker, manager_name, shares, value_usd
        FROM holdings_13f
        WHERE ticker = ?
        """,
        conn,
        params=[ticker],
    )
    hist["value_usd_m"] = hist["value_usd"] / 1_000_000.0
    managers = sorted(hist["manager_name"].dropna().unique().tolist())

    default_watch = [m for m in managers if re.search(r"Vanguard|BlackRock|State Street", m, re.IGNORECASE)]
    watch = st.multiselect("Pick managers to trend", options=managers, default=default_watch[:8] if default_watch else managers[:8])

    trend = hist[hist["manager_name"].isin(watch)].copy()
    if trend.empty:
        st.caption("Pick at least one manager.")
    else:
        pivot = trend.pivot_table(index="quarter_end", columns="manager_name", values="value_usd_m", aggfunc="sum").sort_index()
        st.line_chart(pivot, width="stretch")


# -----------------------------
# Manager view tab
# -----------------------------
with tab_manager:
    st.subheader("Manager View — holdings across your selected universe")

    if manager_choice == "All managers":
        st.info("Use the sidebar Manager Selector to pick a specific manager to view cross-company holdings.")
    else:
        inv = holdings_cur[holdings_cur["manager_name"] == manager_choice].copy()
        inv["value_usd_m"] = (inv["value_usd"] / 1_000_000.0).round(2)
        if "value_change" in inv.columns:
            inv["value_change_m"] = (inv["value_change"] / 1_000_000.0).round(2)

        st.markdown(f"### {manager_choice} — quarter {quarter_end}")
        st.dataframe(
            inv[["ticker", "shares", "value_usd_m", "shares_change", "value_change_m"]],
            width="stretch",
            hide_index=True,
        )


# -----------------------------
# Data / Exports tab
# -----------------------------
with tab_data:
    st.subheader("Data management & exports")

    st.markdown("### Loaded quarters")
    st.dataframe(loaded, width="stretch", hide_index=True)

    st.markdown("### Export current quarter view (CSV)")
    export_df = holdings_view.copy()
    csv = export_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download 13F_current_quarter_view.csv",
        data=csv,
        file_name="13F_current_quarter_view.csv",
        mime="text/csv",
    )

    st.markdown("### Export top holders per company (CSV)")
    topn2 = 25
    top_df = (
        holdings_view.sort_values(["ticker", "value_usd"], ascending=[True, False])
        .groupby("ticker")
        .head(topn2)
        .copy()
    )
    top_csv = top_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        f"Download top_{topn2}_holders_per_company.csv",
        data=top_csv,
        file_name=f"top_{topn2}_holders_per_company.csv",
        mime="text/csv",
    )


# -----------------------------
# Debug tab
# -----------------------------
with tab_debug:
    st.subheader("Debug / Diagnostics")

    st.markdown("### What the pipeline is doing")
    st.write(
        {
            "quarter_end_selected": quarter_end,
            "prior_quarter_end": prior_q,
            "selected_tickers": selected_tickers,
            "ticker_to_cusip": {t: TICKER_TO_CUSIP.get(t) for t in selected_tickers},
            "manager_filter": manager_choice,
            "rows_in_view": int(len(holdings_view)),
        }
    )

    st.markdown("### Recent ingestion errors (if any)")
    err_df = pd.read_sql_query(
        """
        SELECT quarter_label, quarter_end, asof_utc, zip_url, error
        FROM quarter_meta
        WHERE ingest_ok = 0 AND error IS NOT NULL
        ORDER BY asof_utc DESC
        LIMIT 25
        """,
        conn,
    )
    st.dataframe(err_df, width="stretch", hide_index=True)

st.caption(
    "Note: SEC Form 13F is quarterly and may lag filings. "
    "For best results, ingest multiple quarters and use the Company/Manager trend views."
)
