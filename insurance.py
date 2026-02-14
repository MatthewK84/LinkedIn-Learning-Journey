import re
import sqlite3
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

# Primary (reliable) JSON endpoint (no scraping)
YAHOO_QUOTE_SUMMARY_URL = (
    "https://query2.finance.yahoo.com/v10/finance/quoteSummary/{ticker}"
    "?modules=institutionOwnership,fundOwnership,majorHoldersBreakdown&formatted=false"
)

# Backup (HTML holders page) - may be blocked on Streamlit Cloud but kept as fallback
YAHOO_HOLDERS_URL = "https://finance.yahoo.com/quote/{ticker}/holders/"

# Backup cookie/crumb helpers (for when Yahoo requires a session handshake)
YAHOO_HOME_URL = "https://finance.yahoo.com/"
YAHOO_CRUMB_URL = "https://query2.finance.yahoo.com/v1/test/getcrumb"

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/122.0.0.0 Safari/537.36"
)


# ============================================================
# DATA MODEL
# ============================================================

@dataclass
class SnapshotMeta:
    asof_utc: str
    ticker: str
    source: str
    fetch_ok: int
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
            table_name TEXT NOT NULL,
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


# ============================================================
# UTILS
# ============================================================

def _to_number(x) -> Optional[float]:
    if x is None or (isinstance(x, float) and pd.isna(x)):
        return None
    s = str(x).strip()
    if s in ("", "—", "-", "N/A", "nan"):
        return None
    s = s.replace(",", "")
    if s.endswith("%"):
        try:
            return float(s[:-1]) / 100.0
        except Exception:
            return None
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
    tags: List[str] = []
    if not holder_name:
        return tags
    for tag, pattern in custom_rules:
        if re.search(pattern, holder_name, flags=re.IGNORECASE):
            tags.append(tag)
    return tags


def _epoch_to_date(x) -> Optional[str]:
    try:
        if x is None:
            return None
        return datetime.fromtimestamp(int(x), tz=timezone.utc).date().isoformat()
    except Exception:
        return None


def _headers() -> Dict[str, str]:
    return {
        "User-Agent": USER_AGENT,
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Connection": "keep-alive",
    }


# ============================================================
# COOKIE / CRUMB (BACKUP STRATEGY)
# ============================================================

@st.cache_data(show_spinner=False, ttl=6 * 60 * 60)  # cache 6 hours
def get_yahoo_session_and_crumb() -> Tuple[Optional[str], Optional[str]]:
    """
    Best-effort: create a Yahoo session (cookies) + fetch crumb.
    This sometimes helps with endpoints that behave differently without a prior web session.

    Returns: (cookie_header, crumb)
      - cookie_header: a string like "A3=...; B=...; ...", suitable for a "Cookie" header
      - crumb: crumb string (not always needed for quoteSummary, but useful for other Yahoo endpoints)
    """
    sess = requests.Session()
    try:
        # 1) Hit home page to get baseline cookies
        sess.get(YAHOO_HOME_URL, headers=_headers(), timeout=30, allow_redirects=True)

        # 2) Get crumb (requires cookies)
        r = sess.get(YAHOO_CRUMB_URL, headers=_headers(), timeout=30, allow_redirects=True)
        if r.status_code != 200:
            # Still return cookies; crumb may be blocked
            cookie_header = "; ".join([f"{k}={v}" for k, v in sess.cookies.get_dict().items()]) or None
            return cookie_header, None

        crumb = (r.text or "").strip() or None
        cookie_header = "; ".join([f"{k}={v}" for k, v in sess.cookies.get_dict().items()]) or None
        return cookie_header, crumb

    except Exception:
        return None, None


# ============================================================
# FETCHERS
# ============================================================

def _parse_quote_summary_json(js: dict) -> Dict[str, pd.DataFrame]:
    result = (js.get("quoteSummary") or {}).get("result")
    if not result:
        return {}

    root = result[0]
    tables: Dict[str, pd.DataFrame] = {}

    # Major Holders Breakdown (dict-ish)
    mhb = root.get("majorHoldersBreakdown") or {}
    if mhb:
        mhb_rows = [{"Breakdown": k, "Value": v} for k, v in mhb.items()]
        tables["Major Holders"] = pd.DataFrame(mhb_rows)

    # Institutional holders list
    inst = (root.get("institutionOwnership") or {}).get("ownershipList") or []
    if inst:
        inst_rows = []
        for it in inst:
            inst_rows.append(
                {
                    "holder": it.get("organization"),
                    "shares": _to_number(it.get("position")),
                    "reported_date": _epoch_to_date(it.get("reportDate")),
                    "pct_out": _to_number(it.get("pctHeld")),
                    "value_usd": _to_number(it.get("value")),
                }
            )
        tables["Top Holders (Detail)"] = pd.DataFrame(inst_rows)

    # Mutual fund holders list (kept separate)
    fund = (root.get("fundOwnership") or {}).get("ownershipList") or []
    if fund:
        fund_rows = []
        for it in fund:
            fund_rows.append(
                {
                    "holder": it.get("organization"),
                    "shares": _to_number(it.get("position")),
                    "reported_date": _epoch_to_date(it.get("reportDate")),
                    "pct_out": _to_number(it.get("pctHeld")),
                    "value_usd": _to_number(it.get("value")),
                }
            )
        tables["Top Mutual Fund Holders (Detail)"] = pd.DataFrame(fund_rows)

    return tables


def fetch_quote_summary(ticker: str, cookie_header: Optional[str] = None) -> Tuple[int, Optional[str], Dict[str, pd.DataFrame]]:
    """
    Primary strategy: JSON quoteSummary endpoint.
    Returns: (http_status, error, tables)
    """
    url = YAHOO_QUOTE_SUMMARY_URL.format(ticker=ticker)
    headers = _headers()
    if cookie_header:
        headers["Cookie"] = cookie_header

    try:
        r = requests.get(url, headers=headers, timeout=30, allow_redirects=True)
        if r.status_code != 200:
            return r.status_code, f"HTTP {r.status_code} {url}", {}
        js = r.json()
        tables = _parse_quote_summary_json(js)
        if not tables:
            err = (js.get("quoteSummary") or {}).get("error")
            return r.status_code, f"No tables in JSON. error={err}", {}
        return r.status_code, None, tables
    except Exception as e:
        return 0, str(e), {}


def fetch_holders_html(ticker: str, cookie_header: Optional[str] = None) -> Tuple[int, Optional[str], Dict[str, pd.DataFrame]]:
    """
    Backup strategy: scrape HTML holders page (often blocked on hosted envs).
    Returns: (http_status, error, tables)
    """
    url = YAHOO_HOLDERS_URL.format(ticker=ticker)
    headers = _headers()
    if cookie_header:
        headers["Cookie"] = cookie_header

    try:
        r = requests.get(url, headers=headers, timeout=30, allow_redirects=True)
        if r.status_code != 200:
            return r.status_code, f"HTTP {r.status_code} {url}", {}

        tables = pd.read_html(r.text)
        if not tables:
            return r.status_code, "No HTML tables found (blocked/consent/bot page likely).", {}

        out: Dict[str, pd.DataFrame] = {}
        for t in tables:
            t = _clean_columns(t)
            cols = set([c.lower() for c in t.columns])

            if len(t.columns) == 2 and ("breakdown" in cols or "value" in cols):
                out.setdefault("Major Holders", t)

            if {"holder", "shares", "date reported"}.issubset(cols):
                out.setdefault("Top Holders (Detail)", t)

        if not out:
            return r.status_code, "Tables found, but none matched expected holder schemas.", {}

        return r.status_code, None, out

    except Exception as e:
        return 0, str(e), {}


@st.cache_data(show_spinner=False, ttl=60 * 60)
def fetch_holders_tables_with_fallbacks(ticker: str) -> Tuple[SnapshotMeta, Dict[str, pd.DataFrame]]:
    """
    Full strategy:
      1) quoteSummary JSON (no cookies)
      2) quoteSummary JSON with cookie/crumb session (best-effort)
      3) HTML holders scrape with cookie/crumb session (last resort)
    """
    asof = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    # 1) JSON without cookies
    status, err, tables = fetch_quote_summary(ticker, cookie_header=None)
    if tables:
        return SnapshotMeta(asof, ticker, "yahoo_quoteSummary", 1, None), tables

    # 2) JSON with cookie/crumb
    cookie_header, crumb = get_yahoo_session_and_crumb()
    status2, err2, tables2 = fetch_quote_summary(ticker, cookie_header=cookie_header)
    if tables2:
        note = None
        # keep a breadcrumb in error field? no; store nothing when success
        return SnapshotMeta(asof, ticker, "yahoo_quoteSummary_cookie", 1, note), tables2

    # 3) HTML last-resort (often fails on hosted env, but sometimes works)
    status3, err3, tables3 = fetch_holders_html(ticker, cookie_header=cookie_header)
    if tables3:
        return SnapshotMeta(asof, ticker, "yahoo_html_cookie", 1, None), tables3

    # Failure: keep the most informative error
    final_err = f"quoteSummary(no-cookie): {err} | quoteSummary(cookie/crumb={bool(crumb)}): {err2} | html(cookie/crumb={bool(crumb)}): {err3}"
    return SnapshotMeta(asof, ticker, "yahoo_fallbacks", 0, final_err), {}


# ============================================================
# PERSISTENCE
# ============================================================

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

        df_n = df.copy()

        # Normalize if it's one of the detail tables already in canonical schema
        if table_name in ("Top Holders (Detail)", "Top Mutual Fund Holders (Detail)"):
            # Ensure canonical columns exist
            cols = set([c.lower().strip() for c in df_n.columns])
            # If coming from HTML, normalize via column mapping
            if {"holder", "shares", "date reported"}.issubset(cols):
                df_n = _clean_columns(df_n)
                rename_map = {}
                for c in df_n.columns:
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
                df_n = df_n.rename(columns=rename_map)
                keep = [c for c in ["holder", "shares", "reported_date", "pct_out", "value_usd"] if c in df_n.columns]
                df_n = df_n[keep].copy()
                if "shares" in df_n.columns:
                    df_n["shares"] = df_n["shares"].apply(_to_number)
                if "pct_out" in df_n.columns:
                    df_n["pct_out"] = df_n["pct_out"].apply(_to_number)
                if "value_usd" in df_n.columns:
                    df_n["value_usd"] = df_n["value_usd"].apply(_to_number)
                if "reported_date" in df_n.columns:
                    df_n["reported_date"] = pd.to_datetime(df_n["reported_date"], errors="coerce").dt.date.astype(str)

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
                    None if (holder is None or (isinstance(holder, float) and pd.isna(holder))) else str(holder),
                    None if shares is None or (isinstance(shares, float) and pd.isna(shares)) else float(shares),
                    None if reported_date is None or reported_date == "NaT" else str(reported_date),
                    None if pct_out is None or (isinstance(pct_out, float) and pd.isna(pct_out)) else float(pct_out),
                    None if value_usd is None or (isinstance(value_usd, float) and pd.isna(value_usd)) else float(value_usd),
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
    SELECT m.asof_utc, r.ticker, r.table_name, r.holder, r.shares, r.reported_date, r.pct_out, r.value_usd
    FROM holder_rows r
    JOIN snapshot_meta m ON m.snapshot_id = r.snapshot_id
    JOIN latest l ON l.ticker = m.ticker AND l.max_asof = m.asof_utc
    WHERE r.table_name IN ('Top Holders (Detail)', 'Top Mutual Fund Holders (Detail)')
      AND r.holder IS NOT NULL
      AND r.ticker IN ({})
    """.format(",".join(["?"] * len(tickers)))
    return pd.read_sql_query(q, conn, params=tickers)


def load_history(conn: sqlite3.Connection, ticker: str) -> pd.DataFrame:
    q = """
    SELECT m.asof_utc, r.ticker, r.table_name, r.holder, r.shares, r.reported_date, r.pct_out, r.value_usd
    FROM holder_rows r
    JOIN snapshot_meta m ON m.snapshot_id = r.snapshot_id
    WHERE m.fetch_ok = 1
      AND r.table_name IN ('Top Holders (Detail)', 'Top Mutual Fund Holders (Detail)')
      AND r.ticker = ?
      AND r.holder IS NOT NULL
    ORDER BY m.asof_utc ASC
    """
    return pd.read_sql_query(q, conn, params=[ticker])


# ============================================================
# UI
# ============================================================

st.set_page_config(page_title="Ownership: Insurers + Wholesalers", layout="wide")

st.title("Institutional Ownership Tracker — Big Insurers + Wholesalers")
st.caption(
    "Pulls top holders via Yahoo quoteSummary JSON and stores snapshots locally (SQLite) so you can track changes over time."
)

with st.expander("What this dashboard is answering (and how)", expanded=False):
    st.markdown(
        """
**Question:** “Who are the biggest non-insider shareholders of the big 3 insurance companies and wholesalers?”

This app:
- Tracks major institutional / fund holders.
- Highlights the “big three” asset managers (**Vanguard, BlackRock, State Street**) and tags pensions.
- Stores timestamped snapshots (SQLite) so you can track changes over time.

**Primary data method:** Yahoo `quoteSummary` JSON (more reliable than scraping HTML in hosted environments).
**Backup method:** Cookie/crumb session + HTML scrape (last resort).
        """
    )

# Sidebar
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
    with st.spinner("Fetching holders and saving snapshot(s)…"):
        for t in selected_tickers:
            meta, tables = fetch_holders_tables_with_fallbacks(t)
            persist_snapshot(conn, meta, tables)
    st.success("Refresh complete. Snapshots saved.")

# Auto-refresh once per session if DB is empty
if "auto_refreshed" not in st.session_state:
    cnt = pd.read_sql_query("SELECT COUNT(*) AS n FROM snapshot_meta", conn)["n"].iloc[0]
    if cnt == 0:
        for t in selected_tickers:
            meta, tables = fetch_holders_tables_with_fallbacks(t)
            persist_snapshot(conn, meta, tables)
    st.session_state["auto_refreshed"] = True

tab_overview, tab_company, tab_investor, tab_data, tab_debug = st.tabs(
    ["Overview", "Company Detail", "Investor View", "Data / Exports", "Debug"]
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
        latest["pct_out_display"] = (latest["pct_out"] * 100.0).round(3)

        c1, c2 = st.columns([2, 1])

        with c2:
            st.markdown("### Concentration quick check")
            big3 = latest[
                latest["tags"].str.contains("Vanguard|BlackRock|State Street", regex=True, na=False)
            ].copy()
            if not big3.empty and latest["pct_out"].notna().any():
                conc = (
                    big3.groupby("ticker")["pct_out"]
                    .sum()
                    .reset_index()
                    .rename(columns={"pct_out": "big3_pct_out"})
                )
                conc["big3_pct_out"] = (conc["big3_pct_out"] * 100.0).round(3)
                st.dataframe(conc, width="stretch", hide_index=True)
            else:
                st.caption("Big 3 concentration appears once %Out is present in latest rows.")

        with c1:
            st.markdown("### Top holders (latest)")

            min_pct = st.slider("Minimum % Out (latest)", 0.0, 20.0, 0.0, 0.25)
            tag_filter = st.multiselect(
                "Filter by tag",
                options=sorted(
                    {
                        t
                        for ts in latest["tags"].dropna().tolist()
                        for t in [x.strip() for x in ts.split(",") if x.strip()]
                    }
                ),
                default=[],
            )

            view = latest.copy()
            if "pct_out" in view.columns and view["pct_out"].notna().any():
                view = view[(view["pct_out"].fillna(0) * 100.0) >= min_pct]
            if tag_filter:
                view = view[
                    view["holder"].apply(
                        lambda x: any(t in apply_tags(x, tag_rules) for t in tag_filter)
                    )
                ]

            view = view.sort_values(["ticker", "pct_out"], ascending=[True, False])
            st.dataframe(
                view[
                    [
                        "asof_utc",
                        "ticker",
                        "table_name",
                        "holder",
                        "tags",
                        "shares",
                        "reported_date",
                        "pct_out_display",
                        "value_usd",
                    ]
                ],
                width="stretch",
                hide_index=True,
            )

        st.markdown("### Ownership concentration chart (latest)")
        if "pct_out" in latest.columns and latest["pct_out"].notna().any():
            chart_df = latest.dropna(subset=["pct_out"]).copy()
            chart_df["pct_out_pct"] = chart_df["pct_out"] * 100.0
            N = st.selectbox("Top N holders per company", [5, 10, 15, 25], index=1)
            chart_df = (
                chart_df.sort_values(["ticker", "pct_out"], ascending=[True, False])
                .groupby("ticker")
                .head(N)
            )
            st.bar_chart(
                data=chart_df.pivot_table(
                    index="holder", columns="ticker", values="pct_out_pct", aggfunc="max"
                ).fillna(0),
                width="stretch",
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
        hist["pct_out_display"] = (hist["pct_out"] * 100.0).round(3)

        st.markdown("### Latest for this company")
        latest_asof = hist["asof_utc"].max()
        latest_rows = hist[hist["asof_utc"] == latest_asof].sort_values("pct_out", ascending=False)

        st.dataframe(
            latest_rows[
                ["asof_utc", "table_name", "holder", "tags", "shares", "reported_date", "pct_out_display", "value_usd"]
            ],
            width="stretch",
            hide_index=True,
        )

        st.markdown("### Change over time (holder-level)")
        holders = sorted(hist["holder"].dropna().unique().tolist())
        default_watch = [h for h in holders if re.search(r"Vanguard|BlackRock|State Street", h, re.IGNORECASE)]
        watch = st.multiselect("Trend these holders", options=holders, default=default_watch[:10])

        trend = hist[hist["holder"].isin(watch)].copy()
        if trend.empty:
            st.caption("Select one or more holders to trend.")
        else:
            trend["asof_dt"] = pd.to_datetime(trend["asof_utc"])
            trend = trend.sort_values("asof_dt")

            if trend["pct_out"].notna().any():
                pivot = trend.pivot_table(index="asof_dt", columns="holder", values="pct_out", aggfunc="max") * 100.0
                st.line_chart(pivot, width="stretch")
            else:
                pivot = trend.pivot_table(index="asof_dt", columns="holder", values="shares", aggfunc="max")
                st.line_chart(pivot, width="stretch")

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
        inv_df["pct_out_display"] = (inv_df["pct_out"] * 100.0).round(3)

        st.markdown(f"### {investor}")
        st.dataframe(
            inv_df[["asof_utc", "ticker", "table_name", "shares", "reported_date", "pct_out_display", "value_usd", "tags"]],
            width="stretch",
            hide_index=True,
        )

        st.markdown("### Simple narrative cue")
        if inv_df["pct_out"].notna().any():
            tot = (inv_df["pct_out"].fillna(0).sum() * 100.0)
            st.write(
                f"Across the selected universe, this holder accounts for ~**{tot:.3f}%** combined %Out "
                f"(sum of per-company %Out across the latest snapshot)."
            )
        else:
            st.caption("Percent-out not available in latest rows; showing shares/value instead.")

# -----------------------------
# Data / Exports
# -----------------------------
with tab_data:
    st.subheader("Data management & exports")

    meta_df = pd.read_sql_query(
        "SELECT snapshot_id, asof_utc, ticker, source, fetch_ok, error FROM snapshot_meta ORDER BY asof_utc DESC LIMIT 200",
        conn,
    )
    st.markdown("### Recent snapshots")
    st.dataframe(meta_df, width="stretch", hide_index=True)

    st.markdown("### Recent fetch errors (if any)")
    err_df = pd.read_sql_query(
        """
        SELECT asof_utc, ticker, source, error
        FROM snapshot_meta
        WHERE fetch_ok = 0 AND error IS NOT NULL
        ORDER BY asof_utc DESC
        LIMIT 50
        """,
        conn,
    )
    st.dataframe(err_df, width="stretch", hide_index=True)

    st.markdown("### Export latest holders as CSV")
    latest = load_latest_detail(conn, selected_tickers)
    if latest.empty:
        st.caption("Nothing to export yet.")
    else:
        latest["tags"] = latest["holder"].apply(lambda x: ", ".join(apply_tags(x, tag_rules)))
        csv = latest.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download latest_holders.csv",
            data=csv,
            file_name="latest_holders.csv",
            mime="text/csv",
        )

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
        st.dataframe(raw, width="stretch", hide_index=True)

# -----------------------------
# Debug (helps you see what Yahoo is returning)
# -----------------------------
with tab_debug:
    st.subheader("Connectivity diagnostics")
    st.caption("Use this to see whether quoteSummary is reachable from Streamlit Cloud and what errors you’re getting.")

    test_ticker = st.selectbox("Test ticker", options=selected_tickers, index=0)
    cookie_header, crumb = get_yahoo_session_and_crumb()

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### quoteSummary (no cookie)")
        status, err, tables = fetch_quote_summary(test_ticker, cookie_header=None)
        st.write({"status": status, "error": err, "tables": list(tables.keys())})

    with c2:
        st.markdown("### quoteSummary (cookie/crumb)")
        status2, err2, tables2 = fetch_quote_summary(test_ticker, cookie_header=cookie_header)
        st.write({"status": status2, "error": err2, "tables": list(tables2.keys()), "crumb_present": bool(crumb)})

    st.markdown("### HTML holders (cookie/crumb) — last resort")
    status3, err3, tables3 = fetch_holders_html(test_ticker, cookie_header=cookie_header)
    st.write({"status": status3, "error": err3, "tables": list(tables3.keys())})

st.caption("Tip: schedule periodic runs (cron/GitHub Actions) to refresh and build a long ownership history.")
