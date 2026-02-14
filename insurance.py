import re
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

import pandas as pd
import requests
import streamlit as st

# -----------------------------
# Config
# -----------------------------
DEFAULT_COMPANIES = {
    # "Big 3" health insurers (default set; you can add/remove)
    "UnitedHealth Group": "UNH",
    "Elevance Health": "ELV",
    "The Cigna Group": "CI",

    # "Big 3" drug wholesalers
    "McKesson": "MCK",
    "Cencora": "COR",
    "Cardinal Health": "CAH",
}

# Tags you mentioned + a few useful categories.
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

DB_PATH_DEFAULT = "ownership_snapshots.sqlite"

YAHOO_HOLDERS_URL = "https://finance.yahoo.com/quote/{ticker}/holders?p={ticker}"

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/122.0.0.0 Safari/537.36"
)

# -----------------------------
# Data model
# -----------------------------
@dataclass
class SnapshotMeta:
    asof_utc: str          # snapshot time
    ticker: str
    source: str           # e.g. "yahoo_finance"
    fetch_ok: int         # 1/0
    error: Optional[str] = None

# -----------------------------
# DB helpers
# -----------------------------
def db_connect(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn

def db_init(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS snapshot_meta (
            snapshot_id INTEGER PRIMARY KEY AUTOINCREMENT,
            asof_utc TEXT NOT NULL,
            ticker TEXT NOT NULL,
            source TEXT NOT NULL,
            fetch_ok INTEGER NOT NULL,
            error TEXT
        );

        CREATE TABLE IF NOT EXISTS holder_rows (
            row_id INTEGER PRIMARY KEY AUTOINCREMENT,
            snapshot_id INTEGER NOT NULL,
            ticker TEXT NOT NULL,
            table_name TEXT NOT NULL,              -- e.g. "Top Institutional Holders"
            holder TEXT,
            shares REAL,
            reported_date TEXT,
            pct_out REAL,
            value_usd REAL,
            raw_json TEXT,
            FOREIGN KEY(snapshot_id) REFERENCES snapshot_meta(snapshot_id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_holder_rows_ticker_table
        ON holder_rows(ticker, table_name);

        CREATE INDEX IF NOT EXISTS idx_snapshot_meta_ticker_time
        ON snapshot_meta(ticker, asof_utc);
        """
    )
    conn.commit()

# -----------------------------
# Parsing utilities
# -----------------------------
def _to_number(x) -> Optional[float]:
    if x is None or (isinstance(x, float) and pd.isna(x)):
        return None
    s = str(x).strip()
    if s in ("", "—", "-", "N/A", "nan"):
        return None
    # remove commas
    s = s.replace(",", "")
    # handle percents
    if s.endswith("%"):
        try:
            return float(s[:-1]) / 100.0
        except Exception:
            return None
    # handle suffixes like 1.2B / 300M / 20K
    m = re.match(r"^([0-9]*\.?[0-9]+)\s*([KMBT])?$", s, re.IGNORECASE)
    if m:
        val = float(m.group(1))
        suf = (m.group(2) or "").upper()
        mult = {"": 1, "K": 1e3, "M": 1e6, "B": 1e9, "T": 1e12}.get(suf, 1)
        return val * mult
    try:
        return float(s)
    except Exception:
        return None

def _clean_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    return df

def apply_tags(holder_name: str, custom_rules: List[Tuple[str, str]]) -> List[str]:
    tags = []
    if not holder_name:
        return tags
    for tag, pattern in custom_rules:
        if re.search(pattern, holder_name, flags=re.IGNORECASE):
            tags.append(tag)
    return tags

# -----------------------------
# Yahoo fetcher
# -----------------------------
@st.cache_data(show_spinner=False, ttl=60 * 60)  # cache 1 hour
def fetch_yahoo_holders_tables(ticker: str) -> Tuple[SnapshotMeta, Dict[str, pd.DataFrame]]:
    url = YAHOO_HOLDERS_URL.format(ticker=ticker)
    headers = {"User-Agent": USER_AGENT, "Accept-Language": "en-US,en;q=0.9"}
    asof = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    try:
        r = requests.get(url, headers=headers, timeout=30)
        r.raise_for_status()
        html = r.text

        # Yahoo holders pages typically contain multiple tables.
        # We’ll pull them via read_html and then identify by column patterns.
        tables = pd.read_html(html)
        out: Dict[str, pd.DataFrame] = {}

        for t in tables:
            t = _clean_columns(t)

            cols = set([c.lower() for c in t.columns])
            # "Major Holders" has two columns like "Breakdown", "Value"
            if len(t.columns) == 2 and ("breakdown" in cols or "value" in cols):
                out.setdefault("Major Holders", t)

            # Institutional holders table usually includes: Holder, Shares, Date Reported, % Out, Value
            if {"holder", "shares", "date reported"}.issubset(cols):
                if "% out" in cols or "value" in cols:
                    # heuristic: institutional holders table tends to be larger and appears first
                    # We’ll label by whether it looks like "institutional" vs "mutual fund" later if needed.
                    out.setdefault("Top Holders (Detail)", t)

        # Yahoo often provides both "Top Institutional Holders" and "Top Mutual Fund Holders".
        # read_html can merge them; we split using row density + presence of fund-like names as best-effort.
        # If we can’t split confidently, we keep a single detail table.
        meta = SnapshotMeta(asof_utc=asof, ticker=ticker, source="yahoo_finance", fetch_ok=1)
        return meta, out

    except Exception as e:
        meta = SnapshotMeta(asof_utc=asof, ticker=ticker, source="yahoo_finance", fetch_ok=0, error=str(e))
        return meta, {}

def normalize_detail_table(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize to canonical columns:
    holder, shares, reported_date, pct_out, value_usd
    """
    df = df.copy()
    # Standardize column names
    rename_map = {}
    for c in df.columns:
        cl = c.lower().strip()
        if cl == "holder":
            rename_map[c] = "holder"
        elif cl == "shares":
            rename_map[c] = "shares"
        elif cl == "date reported":
            rename_map[c] = "reported_date"
        elif cl in ("% out", "%out", "pct out"):
            rename_map[c] = "pct_out"
        elif cl == "value":
            rename_map[c] = "value_usd"
    df = df.rename(columns=rename_map)

    # Keep only canonical columns (if present)
    keep = [c for c in ["holder", "shares", "reported_date", "pct_out", "value_usd"] if c in df.columns]
    df = df[keep].copy()

    if "shares" in df.columns:
        df["shares"] = df["shares"].apply(_to_number)
    if "pct_out" in df.columns:
        df["pct_out"] = df["pct_out"].apply(_to_number)  # already converted to decimal
    if "value_usd" in df.columns:
        df["value_usd"] = df["value_usd"].apply(_to_number)

    # Normalize reported_date to YYYY-MM-DD if possible (Yahoo often shows "Dec 31, 2025")
    if "reported_date" in df.columns:
        df["reported_date"] = pd.to_datetime(df["reported_date"], errors="coerce").dt.date.astype(str)

    return df

# -----------------------------
# Persistence
# -----------------------------
def persist_snapshot(conn: sqlite3.Connection, meta: SnapshotMeta, tables: Dict[str, pd.DataFrame]) -> int:
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO snapshot_meta (asof_utc, ticker, source, fetch_ok, error) VALUES (?, ?, ?, ?, ?)",
        (meta.asof_utc, meta.ticker, meta.source, meta.fetch_ok, meta.error),
    )
    snapshot_id = cur.lastrowid

    for table_name, df in tables.items():
        if df is None or df.empty:
            continue
        if table_name == "Top Holders (Detail)":
            df_n = normalize_detail_table(df)
        else:
            df_n = df.copy()

        # insert row-by-row
        for _, row in df_n.iterrows():
            holder = row.get("holder") if isinstance(row, pd.Series) else None
            shares = row.get("shares") if isinstance(row, pd.Series) else None
            reported_date = row.get("reported_date") if isinstance(row, pd.Series) else None
            pct_out = row.get("pct_out") if isinstance(row, pd.Series) else None
            value_usd = row.get("value_usd") if isinstance(row, pd.Series) else None

            cur.execute(
                """
                INSERT INTO holder_rows
                (snapshot_id, ticker, table_name, holder, shares, reported_date, pct_out, value_usd, raw_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    snapshot_id,
                    meta.ticker,
                    table_name,
                    None if pd.isna(holder) else str(holder),
                    None if (shares is None or (isinstance(shares, float) and pd.isna(shares))) else float(shares),
                    None if (reported_date is None or reported_date == "NaT") else str(reported_date),
                    None if (pct_out is None or (isinstance(pct_out, float) and pd.isna(pct_out))) else float(pct_out),
                    None if (value_usd is None or (isinstance(value_usd, float) and pd.isna(value_usd))) else float(value_usd),
                    None,
                ),
            )

    conn.commit()
    return snapshot_id

def load_latest_detail(conn: sqlite3.Connection, tickers: List[str]) -> pd.DataFrame:
    q = """
    WITH latest AS (
        SELECT ticker, MAX(asof_utc) AS max_asof
        FROM snapshot_meta
        WHERE fetch_ok = 1
        GROUP BY ticker
    )
    SELECT m.asof_utc, r.ticker, r.holder, r.shares, r.reported_date, r.pct_out, r.value_usd
    FROM holder_rows r
    JOIN snapshot_meta m ON m.snapshot_id = r.snapshot_id
    JOIN latest l ON l.ticker = m.ticker AND l.max_asof = m.asof_utc
    WHERE r.table_name = 'Top Holders (Detail)'
      AND r.holder IS NOT NULL
      AND r.ticker IN ({})
    """.format(",".join(["?"] * len(tickers)))
    return pd.read_sql_query(q, conn, params=tickers)

def load_history(conn: sqlite3.Connection, ticker: str) -> pd.DataFrame:
    q = """
    SELECT m.asof_utc, r.ticker, r.holder, r.shares, r.reported_date, r.pct_out, r.value_usd
    FROM holder_rows r
    JOIN snapshot_meta m ON m.snapshot_id = r.snapshot_id
    WHERE m.fetch_ok = 1
      AND r.table_name = 'Top Holders (Detail)'
      AND r.ticker = ?
      AND r.holder IS NOT NULL
    ORDER BY m.asof_utc ASC
    """
    return pd.read_sql_query(q, conn, params=[ticker])

# -----------------------------
# UI
# -----------------------------
st.set_page_config(page_title="Ownership: Insurers + Wholesalers", layout="wide")

st.title("Institutional Ownership Tracker — Big Insurers + Wholesalers")
st.caption(
    "Pulls top holders from Yahoo Finance 'Holders' pages and stores snapshots locally (SQLite) so you can track changes over time."
)

with st.expander("What this dashboard is answering (and how)", expanded=False):
    st.markdown(
        """
**Question:** “Who are the biggest non-insider shareholders of the big 3 insurance companies and wholesalers?”

This app:
- Tracks **Top Holders (non-insider institutional/mutual fund style holders)**.
- Highlights the recurring “big three” asset managers (**Vanguard, BlackRock, State Street**) and lets you tag state pensions.
- Builds an audit trail via **timestamped snapshots** so you can monitor ownership concentration over time.

Data source: Yahoo Finance “Holders” pages (e.g., UNH/holders). Reporting often reflects institutional filings and can lag.
        """
    )

# Sidebar: configuration
st.sidebar.header("Controls")

db_path = st.sidebar.text_input("SQLite DB Path", DB_PATH_DEFAULT)
conn = db_connect(db_path)
db_init(conn)

companies = DEFAULT_COMPANIES.copy()

st.sidebar.subheader("Company Universe")
selected_names = st.sidebar.multiselect(
    "Track these companies",
    options=list(companies.keys()),
    default=list(companies.keys()),
)
selected_tickers = [companies[n] for n in selected_names]

st.sidebar.subheader("Investor Tag Rules")
tag_rules = DEFAULT_TAG_RULES.copy()
if st.sidebar.toggle("Add a custom tag rule"):
    new_tag = st.sidebar.text_input("Tag name (e.g., 'My Watchlist')", "")
    new_pat = st.sidebar.text_input("Regex pattern (case-insensitive)", "")
    if new_tag and new_pat:
        tag_rules.append((new_tag, new_pat))

st.sidebar.subheader("Data Updates")
col_a, col_b = st.sidebar.columns(2)
do_refresh = col_a.button("Refresh Now")
show_raw = col_b.toggle("Show raw tables", value=False)

if do_refresh:
    with st.spinner("Fetching holder tables and saving snapshot(s)…"):
        for t in selected_tickers:
            meta, tables = fetch_yahoo_holders_tables(t)
            persist_snapshot(conn, meta, tables)
    st.success("Refresh complete. Snapshots saved.")

# Tabs
tab_overview, tab_company, tab_investor, tab_data = st.tabs(
    ["Overview", "Company Detail", "Investor View", "Data / Exports"]
)

# -----------------------------
# Overview
# -----------------------------
with tab_overview:
    st.subheader("Latest snapshot — cross-company view")

    latest = load_latest_detail(conn, selected_tickers)
    if latest.empty:
        st.info("No data yet. Click **Refresh Now** in the sidebar.")
    else:
        latest["tags"] = latest["holder"].apply(lambda x: ", ".join(apply_tags(x, tag_rules)))
        latest["pct_out_display"] = (latest["pct_out"] * 100.0).round(2)

        c1, c2 = st.columns([2, 1])

        with c2:
            st.markdown("### Concentration quick check")
            # Share of %Out for the big 3 managers, by ticker
            big3 = latest[latest["tags"].str.contains("Vanguard|BlackRock|State Street", regex=True, na=False)].copy()
            if not big3.empty and "pct_out" in big3.columns:
                conc = (
                    big3.groupby("ticker")["pct_out"]
                    .sum()
                    .reset_index()
                    .rename(columns={"pct_out": "big3_pct_out"})
                )
                conc["big3_pct_out"] = (conc["big3_pct_out"] * 100.0).round(2)
                st.dataframe(conc, use_container_width=True)
            else:
                st.caption("Big 3 concentration will appear once % Out is available in the latest tables.")

        with c1:
            st.markdown("### Top holders (latest)")

            # filter controls
            min_pct = st.slider("Minimum % Out (latest)", 0.0, 20.0, 0.0, 0.25)
            tag_filter = st.multiselect(
                "Filter by tag",
                options=sorted({t for ts in latest["tags"].dropna().tolist() for t in [x.strip() for x in ts.split(",") if x.strip()]}),
                default=[],
            )

            view = latest.copy()
            if "pct_out" in view.columns:
                view = view[(view["pct_out"].fillna(0) * 100.0) >= min_pct]
            if tag_filter:
                view = view[view["holder"].apply(lambda x: any(t in apply_tags(x, tag_rules) for t in tag_filter))]

            view = view.sort_values(["ticker", "pct_out"], ascending=[True, False])
            st.dataframe(
                view[["asof_utc", "ticker", "holder", "tags", "shares", "reported_date", "pct_out_display", "value_usd"]],
                use_container_width=True,
                hide_index=True,
            )

        st.markdown("### Ownership concentration chart (latest)")
        if "pct_out" in latest.columns and latest["pct_out"].notna().any():
            chart_df = latest.dropna(subset=["pct_out"]).copy()
            chart_df["pct_out_pct"] = chart_df["pct_out"] * 100.0
            # Top N per ticker to keep clean
            N = st.selectbox("Top N holders per company", [5, 10, 15, 25], index=1)
            chart_df = chart_df.sort_values(["ticker", "pct_out"], ascending=[True, False]).groupby("ticker").head(N)

            st.bar_chart(
                data=chart_df.pivot_table(index="holder", columns="ticker", values="pct_out_pct", aggfunc="max").fillna(0),
                use_container_width=True,
            )
        else:
            st.caption("Percent-out chart will appear once % Out is available.")

# -----------------------------
# Company Detail
# -----------------------------
with tab_company:
    st.subheader("Company Detail — snapshot history")

    ticker = st.selectbox("Choose a company", options=selected_tickers, index=0)
    hist = load_history(conn, ticker)

    if hist.empty:
        st.info("No history for this ticker yet. Click **Refresh Now**.")
    else:
        hist["tags"] = hist["holder"].apply(lambda x: ", ".join(apply_tags(x, tag_rules)))
        hist["pct_out_display"] = (hist["pct_out"] * 100.0).round(2)

        st.markdown("### Latest for this company")
        latest_asof = hist["asof_utc"].max()
        latest_rows = hist[hist["asof_utc"] == latest_asof].sort_values("pct_out", ascending=False)

        st.dataframe(
            latest_rows[["asof_utc", "holder", "tags", "shares", "reported_date", "pct_out_display", "value_usd"]],
            use_container_width=True,
            hide_index=True,
        )

        st.markdown("### Change over time (holder-level)")
        # pick a few holders to trend
        holders = sorted(hist["holder"].dropna().unique().tolist())
        default_watch = [h for h in holders if re.search(r"Vanguard|BlackRock|State Street", h, re.IGNORECASE)]
        watch = st.multiselect("Trend these holders", options=holders, default=default_watch[:10])

        trend = hist[hist["holder"].isin(watch)].copy()
        if trend.empty:
            st.caption("Select one or more holders to trend.")
        else:
            trend["asof_dt"] = pd.to_datetime(trend["asof_utc"])
            trend = trend.sort_values("asof_dt")
            # plot with Streamlit native line chart
            if "pct_out" in trend.columns and trend["pct_out"].notna().any():
                pivot = trend.pivot_table(index="asof_dt", columns="holder", values="pct_out", aggfunc="max") * 100.0
                st.line_chart(pivot, use_container_width=True)
            else:
                pivot = trend.pivot_table(index="asof_dt", columns="holder", values="shares", aggfunc="max")
                st.line_chart(pivot, use_container_width=True)

# -----------------------------
# Investor View
# -----------------------------
with tab_investor:
    st.subheader("Investor View — across companies")

    latest = load_latest_detail(conn, selected_tickers)
    if latest.empty:
        st.info("No data yet. Click **Refresh Now**.")
    else:
        latest["tags"] = latest["holder"].apply(lambda x: ", ".join(apply_tags(x, tag_rules)))
        holder_list = sorted(latest["holder"].dropna().unique().tolist())

        investor = st.selectbox(
            "Choose an investor / institution",
            options=holder_list,
            index=0 if holder_list else None,
        )

        inv_df = latest[latest["holder"] == investor].copy()
        inv_df["pct_out_display"] = (inv_df["pct_out"] * 100.0).round(2)

        st.markdown(f"### {investor}")
        st.dataframe(
            inv_df[["asof_utc", "ticker", "shares", "reported_date", "pct_out_display", "value_usd", "tags"]],
            use_container_width=True,
            hide_index=True,
        )

        st.markdown("### Simple narrative cue")
        if inv_df["pct_out"].notna().any():
            tot = (inv_df["pct_out"].fillna(0).sum() * 100.0)
            st.write(f"Across the selected universe, this holder accounts for ~**{tot:.2f}%** combined %Out (sum of per-company %Out).")
        else:
            st.caption("Percent-out not available in latest rows; showing shares/value instead.")

# -----------------------------
# Data / Exports
# -----------------------------
with tab_data:
    st.subheader("Data management & exports")

    # Snapshot table
    meta_df = pd.read_sql_query(
        "SELECT snapshot_id, asof_utc, ticker, source, fetch_ok, error FROM snapshot_meta ORDER BY asof_utc DESC LIMIT 200",
        conn,
    )
    st.markdown("### Recent snapshots")
    st.dataframe(meta_df, use_container_width=True, hide_index=True)

    st.markdown("### Export latest holders as CSV")
    latest = load_latest_detail(conn, selected_tickers)
    if latest.empty:
        st.caption("Nothing to export yet.")
    else:
        latest["tags"] = latest["holder"].apply(lambda x: ", ".join(apply_tags(x, tag_rules)))
        csv = latest.to_csv(index=False).encode("utf-8")
        st.download_button("Download latest_holders.csv", data=csv, file_name="latest_holders.csv", mime="text/csv")

    if show_raw:
        st.markdown("### Raw holder_rows (most recent 200)")
        raw = pd.read_sql_query(
            """
            SELECT r.row_id, m.asof_utc, r.ticker, r.table_name, r.holder, r.shares, r.reported_date, r.pct_out, r.value_usd
            FROM holder_rows r
            JOIN snapshot_meta m ON m.snapshot_id = r.snapshot_id
            ORDER BY r.row_id DESC
            LIMIT 200
            """,
            conn,
        )
        st.dataframe(raw, use_container_width=True, hide_index=True)

st.caption("Tip: schedule periodic runs (cron/GitHub Actions) to refresh and build a long ownership history.")
