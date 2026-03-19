import streamlit as st
import yfinance as yf
import anthropic
import json
import pandas as pd
from datetime import datetime, timedelta
from plotly.graph_objs import Figure, Scatter

st.set_page_config(
    page_title="NorthBrief",
    page_icon="◆",
    layout="wide",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Familjen+Grotesk:wght@400;500;700&family=Instrument+Mono:wght@400;500&display=swap');

:root {
    --bg: #1C1F26; --panel: #13151A; --border: #2A2D35;
    --teal: #00C9A0; --teal-dark: #004D3D; --teal-dim: #003D31;
    --red: #E05050; --red-dim: #3D1515;
    --text: #F0F2F5; --muted: #8A8F9E; --dim: #3D4250;
    --amber: #E8A020;
}
html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important; color: var(--text);
    font-family: 'Familjen Grotesk', sans-serif;
}
[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stSidebar"] { background: var(--panel) !important; border-right: 1px solid var(--border) !important; }
[data-testid="stSidebar"] * { color: var(--text) !important; }
[data-testid="stSidebarContent"] { padding: 1.5rem 1.2rem !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }

/* NAV */
.nb-nav { background: var(--panel); padding: 0.9rem 2rem; display: flex; align-items: center;
    justify-content: space-between; border-bottom: 1px solid var(--border); }
.nb-logo { display: flex; align-items: center; gap: 9px; }
.nb-hex { width: 20px; height: 20px; background: var(--teal);
    clip-path: polygon(50% 0%,100% 25%,100% 75%,50% 100%,0% 75%,0% 25%); }
.nb-wordmark { font-size: 1rem; font-weight: 700; color: var(--text); }
.nb-live { display: flex; align-items: center; gap: 6px;
    font-family: 'Instrument Mono', monospace; font-size: 0.57rem;
    letter-spacing: 0.16em; color: var(--dim); text-transform: uppercase; }
.live-dot { width: 6px; height: 6px; background: var(--teal); border-radius: 50%;
    animation: pulse 2s infinite; }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.3} }

/* TABS */
.nb-tabs { background: var(--panel); padding: 0 2rem;
    border-bottom: 1px solid var(--border); display: flex; gap: 0; }
.nb-tab { font-family: 'Instrument Mono', monospace; font-size: 0.6rem; letter-spacing: 0.14em;
    text-transform: uppercase; padding: 0.8rem 1.2rem; color: var(--dim);
    border-bottom: 2px solid transparent; cursor: pointer; transition: all 0.15s; }
.nb-tab.active { color: var(--teal); border-bottom-color: var(--teal); }

/* TICKER BAND */
.ticker-band { background: var(--teal); padding: 1rem 2rem;
    display: flex; align-items: center; justify-content: space-between; }
.tb-name { font-size: 1.4rem; font-weight: 700; color: var(--panel); line-height: 1; margin-bottom: 3px; }
.tb-meta { font-family: 'Instrument Mono', monospace; font-size: 0.57rem;
    letter-spacing: 0.12em; color: var(--teal-dark); text-transform: uppercase; }
.tb-price { font-size: 2rem; font-weight: 700; color: var(--panel); line-height: 1; }
.tb-chg { font-family: 'Instrument Mono', monospace; font-size: 0.7rem; color: var(--teal-dark); margin-left: 10px; }
.badge { display: inline-block; font-family: 'Instrument Mono', monospace; font-size: 0.5rem;
    letter-spacing: 0.14em; text-transform: uppercase; padding: 3px 10px;
    border-radius: 20px; background: var(--teal-dim); color: var(--teal); margin-left: 10px; vertical-align: middle; }
.badge-bear { background: var(--red-dim); color: var(--red); }
.badge-neutral { background: #2A2510; color: var(--amber); }

/* STATS STRIP */
.stats-strip { background: var(--panel); display: grid;
    grid-template-columns: repeat(6, 1fr); border-bottom: 1px solid var(--border); }
.smet { padding: 0.65rem 1rem; border-right: 1px solid var(--border); }
.smet:last-child { border-right: none; }
.smlbl { font-family: 'Instrument Mono', monospace; font-size: 0.5rem;
    letter-spacing: 0.12em; text-transform: uppercase; color: var(--dim); margin-bottom: 3px; }
.smval { font-family: 'Instrument Mono', monospace; font-size: 0.82rem; font-weight: 500; color: var(--text); }

/* CONTENT */
.nb-content { padding: 1.6rem 2rem; }

/* DYNAMIC ROW */
.dyn-row { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem; margin-bottom: 1rem; }
.dyn-card { background: var(--panel); border-radius: 8px; padding: 1.2rem 1.4rem; border: 1px solid var(--border); }
.dyn-lbl { font-family: 'Instrument Mono', monospace; font-size: 0.52rem;
    letter-spacing: 0.16em; text-transform: uppercase; color: var(--dim); margin-bottom: 0.8rem; }
.range-track { height: 4px; background: var(--border); border-radius: 2px; position: relative; margin: 1rem 0 0.5rem; }
.range-fill { height: 4px; background: var(--teal); border-radius: 2px; }
.range-thumb { width: 12px; height: 12px; background: var(--teal); border-radius: 50%;
    position: absolute; top: -4px; transform: translateX(-50%); border: 2px solid var(--bg); }
.range-labels { display: flex; justify-content: space-between; }
.rlbl { font-family: 'Instrument Mono', monospace; font-size: 0.57rem; color: var(--dim); }
.range-current { font-family: 'Instrument Mono', monospace; font-size: 0.7rem; color: var(--teal); text-align: center; margin-top: 4px; }
.range-pct { font-family: 'Instrument Mono', monospace; font-size: 0.57rem; color: var(--dim); text-align: center; }
.upside-num { font-size: 2rem; font-weight: 700; color: var(--teal);
    font-family: 'Instrument Mono', monospace; line-height: 1; margin-bottom: 4px; }
.upside-num.neg { color: var(--red); }
.upside-sub { font-family: 'Instrument Mono', monospace; font-size: 0.57rem; color: var(--dim); }
.upside-detail { margin-top: 0.8rem; display: flex; justify-content: space-between;
    padding-top: 0.8rem; border-top: 1px solid var(--border); }
.ud-lbl { font-family: 'Instrument Mono', monospace; font-size: 0.5rem;
    letter-spacing: 0.1em; text-transform: uppercase; color: var(--dim); margin-bottom: 3px; }
.ud-val { font-family: 'Instrument Mono', monospace; font-size: 0.78rem; font-weight: 500; color: var(--text); }
.gauge-bars { display: flex; align-items: flex-end; gap: 3px; height: 44px; margin-bottom: 6px; }
.gauge-lbl { font-family: 'Instrument Mono', monospace; font-size: 0.7rem;
    font-weight: 500; letter-spacing: 0.1em; text-transform: uppercase; }
.gauge-sub { font-family: 'Instrument Mono', monospace; font-size: 0.54rem; color: var(--dim); margin-top: 2px; }

/* EARNINGS */
.earnings-box { text-align: center; padding: 0.4rem 0; }
.earnings-num { font-size: 2.4rem; font-weight: 700; color: var(--teal);
    font-family: 'Instrument Mono', monospace; line-height: 1; }
.earnings-lbl { font-family: 'Instrument Mono', monospace; font-size: 0.57rem; color: var(--dim); margin-top: 4px; }
.earnings-date { font-family: 'Instrument Mono', monospace; font-size: 0.65rem; color: var(--muted); margin-top: 8px; }

/* BRIEF CARDS */
.overview-card { background: var(--panel); border-radius: 8px; padding: 1.2rem 1.4rem;
    border: 1px solid var(--border); margin-bottom: 1rem; border-left: 3px solid var(--dim); }
.cards-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1rem; }
.card { background: var(--panel); border-radius: 8px; padding: 1.2rem 1.4rem; border: 1px solid var(--border); }
.card-bull { border-top: 2px solid var(--teal); }
.card-bear { border-top: 2px solid var(--red); }
.verdict-card { background: var(--teal-dim); border-radius: 8px;
    padding: 1.4rem 1.6rem; border: 1px solid var(--teal); margin-bottom: 1rem; }
.slbl { font-family: 'Instrument Mono', monospace; font-size: 0.55rem;
    letter-spacing: 0.18em; text-transform: uppercase; font-weight: 500; margin-bottom: 10px; }
.l-snap { color: var(--dim); } .l-bull { color: var(--teal); }
.l-bear { color: var(--red); } .l-verdict { color: var(--teal); }
.l-peer { color: var(--amber); } .l-move { color: #C084FC; }
.sbody { font-size: 0.86rem; line-height: 1.75; color: var(--muted); }
.sbody-verdict { font-size: 0.86rem; line-height: 1.75; color: #A8EFE0; }
.krisk { margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(0,201,160,0.2);
    font-family: 'Instrument Mono', monospace; font-size: 0.6rem; color: var(--dim); }
.krisk span { color: var(--teal); }

/* PEER TABLE */
.peer-table { width: 100%; border-collapse: collapse; margin-top: 0.5rem; }
.peer-table th { font-family: 'Instrument Mono', monospace; font-size: 0.5rem;
    letter-spacing: 0.12em; text-transform: uppercase; color: var(--dim);
    padding: 0.4rem 0.6rem; border-bottom: 1px solid var(--border); text-align: right; }
.peer-table th:first-child { text-align: left; }
.peer-table td { font-family: 'Instrument Mono', monospace; font-size: 0.72rem;
    color: var(--muted); padding: 0.5rem 0.6rem; border-bottom: 1px solid var(--border); text-align: right; }
.peer-table td:first-child { text-align: left; color: var(--text); font-weight: 500; }
.peer-table tr.highlight td { color: var(--teal); }
.peer-table tr:last-child td { border-bottom: none; }

/* BULL/BEAR HISTORY */
.history-row { display: flex; align-items: center; gap: 0.8rem; padding: 0.5rem 0;
    border-bottom: 1px solid var(--border); }
.history-row:last-child { border-bottom: none; }
.hist-date { font-family: 'Instrument Mono', monospace; font-size: 0.6rem; color: var(--dim); width: 80px; }
.hist-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.hist-label { font-family: 'Instrument Mono', monospace; font-size: 0.6rem; font-weight: 500; }
.hist-snippet { font-size: 0.78rem; color: var(--muted); flex: 1; }

/* PORTFOLIO */
.port-row { display: grid; grid-template-columns: 1fr 80px 80px 80px 90px;
    gap: 0.5rem; align-items: center; padding: 0.6rem 0.8rem;
    border-bottom: 1px solid var(--border); }
.port-row:last-child { border-bottom: none; }
.port-header { background: var(--bg); border-radius: 6px 6px 0 0; }
.port-ticker { font-family: 'Instrument Mono', monospace; font-size: 0.72rem; font-weight: 500; color: var(--text); }
.port-name { font-size: 0.7rem; color: var(--dim); }
.port-val { font-family: 'Instrument Mono', monospace; font-size: 0.72rem; color: var(--muted); text-align: right; }
.port-badge { font-family: 'Instrument Mono', monospace; font-size: 0.5rem;
    letter-spacing: 0.1em; text-transform: uppercase; padding: 2px 8px;
    border-radius: 20px; text-align: center; }

/* WHY MOVED */
.move-card { background: var(--panel); border-radius: 8px; padding: 1.4rem 1.6rem;
    border: 1px solid var(--border); border-left: 3px solid #C084FC; }

/* SECTION HEADERS */
.section-hdr { font-family: 'Instrument Mono', monospace; font-size: 0.6rem;
    letter-spacing: 0.18em; text-transform: uppercase; color: var(--dim);
    margin: 1.5rem 0 0.8rem; padding-bottom: 0.5rem; border-bottom: 1px solid var(--border); }

/* FOOTER */
.nb-footer { background: var(--panel); border-top: 1px solid var(--border);
    padding: 0.7rem 2rem; display: flex; justify-content: space-between; align-items: center; }
.ftxt { font-family: 'Instrument Mono', monospace; font-size: 0.55rem;
    letter-spacing: 0.1em; color: var(--dim); text-transform: uppercase; }
.fclock { font-family: 'Instrument Mono', monospace; font-size: 0.55rem; color: var(--teal); }

/* STREAMLIT OVERRIDES */
.stButton > button {
    background: var(--teal) !important; color: var(--panel) !important;
    border: none !important; font-family: 'Instrument Mono', monospace !important;
    font-size: 0.6rem !important; letter-spacing: 0.12em !important;
    text-transform: uppercase !important; padding: 0.6rem 1.5rem !important;
    border-radius: 5px !important; font-weight: 500 !important;
}
.stButton > button:hover { opacity: 0.85 !important; }
.stTextInput > div > div > input {
    background: var(--panel) !important; border: 1px solid var(--border) !important;
    border-radius: 5px !important; color: var(--teal) !important;
    font-family: 'Instrument Mono', monospace !important;
    font-size: 0.9rem !important; letter-spacing: 0.06em !important;
}
.stTextInput > div > div > input:focus { border-color: var(--teal) !important; }
.stTextInput > label { display: none !important; }
.stTabs [data-baseweb="tab-list"] {
    background: var(--panel) !important; border-bottom: 1px solid var(--border) !important; gap: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important; color: var(--dim) !important;
    font-family: 'Instrument Mono', monospace !important; font-size: 0.6rem !important;
    letter-spacing: 0.14em !important; text-transform: uppercase !important;
    border-bottom: 2px solid transparent !important;
}
.stTabs [aria-selected="true"] { color: var(--teal) !important; border-bottom-color: var(--teal) !important; }
.stTabs [data-baseweb="tab-panel"] { background: var(--bg) !important; padding: 0 !important; }
.stRadio > label { color: var(--muted) !important; font-family: 'Instrument Mono', monospace !important; font-size: 0.7rem !important; }
.stRadio [data-testid="stMarkdownContainer"] p { color: var(--muted) !important; font-family: 'Instrument Mono', monospace !important; font-size: 0.7rem !important; }
div[data-testid="stMarkdownContainer"] p { margin: 0 !important; }
.sidebar-lbl { font-family: 'Instrument Mono', monospace; font-size: 0.57rem;
    letter-spacing: 0.14em; text-transform: uppercase; color: var(--dim); margin-bottom: 5px; margin-top: 1rem; }
.sidebar-hint { font-family: 'Instrument Mono', monospace; font-size: 0.57rem;
    color: var(--dim); margin-top: 4px; line-height: 1.6; }

/* CONVICTION SCORE */
.conviction-wrap { display: flex; align-items: center; gap: 1.2rem; margin-bottom: 1rem; }
.conviction-score { font-family: 'Instrument Mono', monospace; font-size: 3rem; font-weight: 500; color: var(--teal); line-height: 1; }
.conviction-score-denom { font-size: 1.2rem; color: var(--dim); }
.conviction-label { font-family: 'Familjen Grotesk', sans-serif; font-size: 1.1rem; font-weight: 700; color: var(--text); margin-bottom: 4px; }
.conviction-rationale { font-size: 0.82rem; color: var(--muted); line-height: 1.6; }
.conviction-bar-track { height: 6px; background: var(--border); border-radius: 3px; margin-top: 0.8rem; }
.conviction-bar-fill { height: 6px; border-radius: 3px; }
.market-implied { display: inline-flex; align-items: center; gap: 6px; font-family: 'Instrument Mono', monospace; font-size: 0.62rem; letter-spacing: 0.12em; text-transform: uppercase; padding: 4px 12px; border-radius: 4px; margin-top: 0.6rem; }
.mi-over { background: #3D1515; color: var(--red); }
.mi-fair { background: #2A2510; color: var(--amber); }
.mi-under { background: var(--teal-dim); color: var(--teal); }

/* DRIVERS */
.drivers-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1rem; }
.driver-card { background: var(--panel); border-radius: 8px; padding: 1.1rem 1.3rem; border: 1px solid var(--border); }
.driver-item { display: flex; align-items: flex-start; gap: 8px; padding: 0.4rem 0; border-bottom: 1px solid var(--border); }
.driver-item:last-child { border-bottom: none; padding-bottom: 0; }
.driver-dot { width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0; margin-top: 6px; }
.driver-txt { font-size: 0.82rem; color: var(--muted); line-height: 1.5; }

/* WHAT WOULD CHANGE */
.wtc-card { background: var(--panel); border-radius: 8px; padding: 1.2rem 1.4rem; border: 1px solid var(--border); border-left: 3px solid var(--amber); margin-bottom: 1rem; }

/* WHAT CHANGED */
.wc-card { background: #0F1208; border-radius: 8px; padding: 1.2rem 1.4rem; border: 1px solid #3A4020; border-left: 3px solid #8FBF30; margin-bottom: 1rem; }
.wc-shift { display: flex; align-items: center; gap: 8px; margin-bottom: 0.6rem; }
.wc-pill { font-family: 'Instrument Mono', monospace; font-size: 0.6rem; letter-spacing: 0.1em; text-transform: uppercase; padding: 2px 8px; border-radius: 3px; }
.wc-from { background: var(--border); color: var(--dim); }
.wc-to { background: #1A2008; border: 1px solid #3A4020; color: #8FBF30; }
.wc-arrow { color: #8FBF30; }

/* WATCHLIST */
.wl-row { display: grid; grid-template-columns: 1fr 90px 90px 100px 110px 44px; align-items: center; padding: 0.65rem 1rem; border-bottom: 1px solid var(--border); gap: 0.5rem; }
.wl-row:last-child { border-bottom: none; }
.wl-ticker { font-family: 'Instrument Mono', monospace; font-size: 0.78rem; font-weight: 500; color: var(--text); }
.wl-name { font-size: 0.7rem; color: var(--dim); margin-top: 1px; }
.wl-val { font-family: 'Instrument Mono', monospace; font-size: 0.75rem; color: var(--muted); text-align: right; }
.wl-badge { font-family: 'Instrument Mono', monospace; font-size: 0.5rem; letter-spacing: 0.1em; text-transform: uppercase; padding: 3px 8px; border-radius: 20px; text-align: center; white-space: nowrap; }
.wl-empty { font-family: 'Instrument Mono', monospace; font-size: 0.65rem; color: var(--dim); text-align: center; padding: 2rem; }

/* YOUR VIEW vs MARKET */
.view-compare { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1rem; }
.view-card { background: var(--panel); border-radius: 8px; padding: 1rem 1.2rem; border: 1px solid var(--border); text-align: center; }
.view-lbl { font-family: 'Instrument Mono', monospace; font-size: 0.55rem; letter-spacing: 0.14em; text-transform: uppercase; color: var(--dim); margin-bottom: 0.6rem; }
.view-val { font-size: 1.1rem; font-weight: 700; }
.view-sub { font-family: 'Instrument Mono', monospace; font-size: 0.58rem; color: var(--dim); margin-top: 4px; }
</style>
""", unsafe_allow_html=True)

# ── HELPERS ───────────────────────────────────────────────────────────────────
def fmt_cap(v):
    if v is None: return "—"
    if v >= 1e9: return f"${v/1e9:.1f}B"
    return f"${v/1e6:.0f}M"

def fmt_pct(v, plus=True):
    if v is None: return "—"
    sign = "+" if (v > 0 and plus) else ""
    return f"{sign}{v*100:.1f}%"

def fmt_x(v):
    if v is None: return "—"
    return f"{v:.1f}x"

def fmt_p(v):
    if v is None: return "—"
    return f"${v:.2f}"

def fetch_data(ticker):
    t = yf.Ticker(ticker)
    info = t.info
    hist_1y = t.history(period="1y")
    hist_1m = t.history(period="1mo")
    hist_1w = t.history(period="7d")
    try:
        cal = t.calendar
        next_earnings = None
        if cal is not None and not cal.empty:
            if 'Earnings Date' in cal.index:
                ed = cal.loc['Earnings Date']
                next_earnings = pd.to_datetime(ed.iloc[0]) if hasattr(ed, 'iloc') else pd.to_datetime(ed)
    except:
        next_earnings = None
    try:
        news = [n.get('title','') for n in (t.news or [])[:6]]
    except:
        news = []
    price_1y = None
    if not hist_1y.empty and len(hist_1y) > 1:
        price_1y = (hist_1y['Close'].iloc[-1] - hist_1y['Close'].iloc[0]) / hist_1y['Close'].iloc[0]
    return {
        "symbol": ticker.upper(),
        "name": info.get("shortName", ticker),
        "sector": info.get("sector", ""),
        "industry": info.get("industry", ""),
        "price": info.get("currentPrice") or info.get("regularMarketPrice"),
        "prev_close": info.get("previousClose"),
        "mkt_cap": info.get("marketCap"),
        "pe": info.get("trailingPE"),
        "fpe": info.get("forwardPE"),
        "ps": info.get("priceToSalesTrailing12Months"),
        "pb": info.get("priceToBook"),
        "ev_ebitda": info.get("enterpriseToEbitda"),
        "rev_growth": info.get("revenueGrowth"),
        "gross_margin": info.get("grossMargins"),
        "op_margin": info.get("operatingMargins"),
        "net_margin": info.get("profitMargins"),
        "roe": info.get("returnOnEquity"),
        "de": info.get("debtToEquity"),
        "cr": info.get("currentRatio"),
        "52h": info.get("fiftyTwoWeekHigh"),
        "52l": info.get("fiftyTwoWeekLow"),
        "target": info.get("targetMeanPrice"),
        "rec": info.get("recommendationKey","").upper(),
        "desc": info.get("longBusinessSummary","")[:500],
        "exchange": info.get("exchange","TSX"),
        "hist_1y": hist_1y, "hist_1m": hist_1m, "hist_1w": hist_1w,
        "next_earnings": next_earnings,
        "news": news,
        "price_1y": price_1y,
        "beta": info.get("beta"),
        "eps": info.get("trailingEps"),
        "avg_volume": info.get("averageVolume"),
    }

def get_peers(sector, exchange, exclude):
    peer_map = {
        "Technology": ["SHOP.TO","CSU.TO","OTEX.TO","BB.TO","AAPL","MSFT"],
        "Energy": ["CNQ.TO","SU.TO","CVE.TO","TOU.TO","IMO.TO"],
        "Financials": ["RY.TO","TD.TO","BNS.TO","BMO.TO","CM.TO"],
        "Consumer Cyclical": ["ATD.TO","MRU.TO","L.TO","CTC-A.TO"],
        "Industrials": ["CNR.TO","CP.TO","TFI.TO","WSP.TO"],
        "Materials": ["ABX.TO","AEM.TO","WPM.TO","FM.TO"],
        "Real Estate": ["BN.TO","BAM.TO","HR-UN.TO","AP-UN.TO"],
        "Healthcare": ["CSH-UN.TO","CTC.TO"],
        "Communication Services": ["BCE.TO","T.TO","QBR-B.TO"],
        "Utilities": ["FTS.TO","EMA.TO","H.TO"],
    }
    peers = [p for p in peer_map.get(sector, []) if p != exclude][:4]
    return peers

def build_brief_prompt(d, prev_snapshot=None):
    prev_context = ""
    if prev_snapshot:
        prev_context = f"""
PREVIOUS SNAPSHOT (for change analysis):
Date: {prev_snapshot.get('date','—')}
Positioning: {prev_snapshot.get('positioning','—')} | Conviction: {prev_snapshot.get('conviction','—')}/10
P/E was: {prev_snapshot.get('pe','—')} | Rev Growth was: {prev_snapshot.get('rev_growth','—')}
Prior verdict: {prev_snapshot.get('verdict','—')}
"""
    return f"""You are a senior equity analyst at a top-tier institutional firm. Return ONLY valid JSON, no markdown.

STOCK: {d['name']} ({d['symbol']}) | {d['sector']} | {d['industry']}
Price: {fmt_p(d['price'])} | Cap: {fmt_cap(d['mkt_cap'])} | 52W: {fmt_p(d['52l'])}-{fmt_p(d['52h'])}
P/E: {fmt_x(d['pe'])} | Fwd P/E: {fmt_x(d['fpe'])} | EV/EBITDA: {fmt_x(d['ev_ebitda'])}
Rev Growth: {fmt_pct(d['rev_growth'])} | Gross Margin: {fmt_pct(d['gross_margin'])} | Op Margin: {fmt_pct(d['op_margin'])}
ROE: {fmt_pct(d['roe'])} | D/E: {d['de'] if d['de'] else 'n/a'} | Beta: {d['beta'] if d['beta'] else 'n/a'}
1Y Return: {fmt_pct(d['price_1y'])} | Target: {fmt_p(d['target'])} | Consensus: {d['rec']}
Business: {d['desc']}
Recent headlines: {'; '.join(d['news'][:4])}
{prev_context}

Return JSON (all fields required):
{{
  "summary": "2-3 specific sentences on what the company does and current standing.",
  "bull_case": "3-4 sentences with specific metrics supporting optimism.",
  "bear_case": "3-4 sentences with specific risks and weaknesses.",
  "verdict": "1-2 direct sentences on risk/reward at current levels.",
  "key_risk": "Single biggest risk in one sentence.",
  "why_moved": "2-3 sentences explaining the most likely drivers of recent price movement.",
  "positioning": "one of: Strongly Bullish / Moderately Bullish / Neutral / Moderately Bearish / Strongly Bearish",
  "conviction": 7,
  "conviction_rationale": "One sentence explaining the conviction score.",
  "upside_drivers": ["driver 1", "driver 2", "driver 3"],
  "downside_drivers": ["risk 1", "risk 2", "risk 3"],
  "what_would_change": "2-3 sentences on specific catalysts that would flip this positioning.",
  "market_implied_view": "one of: Overvalued / Fair Value / Undervalued",
  "sentiment": "BULLISH or BEARISH or NEUTRAL",
  "peer_context": "1-2 sentences on valuation vs sector peers.",
  "what_changed": "If previous snapshot provided describe what changed materially. Otherwise: First analysis for this ticker."
}}"""

def build_portfolio_prompt(tickers_data):
    summaries = []
    for sym, d in tickers_data.items():
        summaries.append(f"{sym}: {d['sector']}, P/E {fmt_x(d['pe'])}, Rev Growth {fmt_pct(d['rev_growth'])}, 1Y Return {fmt_pct(d['price_1y'])}")
    return f"""You are a portfolio analyst. Analyse this portfolio and return ONLY valid JSON.

Holdings:
{chr(10).join(summaries)}

Return JSON:
{{
  "overall_sentiment": "BULLISH or BEARISH or NEUTRAL",
  "summary": "2-3 sentences on the overall portfolio positioning.",
  "biggest_risk": "The single biggest risk across the portfolio in one sentence.",
  "best_positioned": "The ticker symbol best positioned for near-term performance.",
  "most_exposed": "The ticker symbol most exposed to downside risk.",
  "diversification": "1-2 sentences on portfolio diversification quality."
}}"""

def call_claude(prompt, api_key):
    client = anthropic.Anthropic(api_key=api_key)
    msg = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1200,
        messages=[{"role": "user", "content": prompt}]
    )
    raw = msg.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"): raw = raw[4:]
    return json.loads(raw.strip())

def save_snapshot(symbol, d, brief):
    """Save a snapshot of current brief data for change tracking."""
    key = f"snapshot_{symbol}"
    if key not in st.session_state:
        st.session_state[key] = []
    snap = {
        "date": datetime.now().strftime("%b %d, %Y %H:%M"),
        "positioning": brief.get("positioning","—"),
        "sentiment": brief.get("sentiment","NEUTRAL"),
        "conviction": brief.get("conviction", 5),
        "pe": fmt_x(d.get("pe")),
        "rev_growth": fmt_pct(d.get("rev_growth")),
        "price": fmt_p(d.get("price")),
        "verdict": brief.get("verdict","")[:120],
    }
    st.session_state[key].append(snap)
    st.session_state[key] = st.session_state[key][-10:]

def get_prev_snapshot(symbol):
    key = f"snapshot_{symbol}"
    snaps = st.session_state.get(key, [])
    return snaps[-2] if len(snaps) >= 2 else None

def add_to_watchlist(symbol, name, sector):
    if "watchlist" not in st.session_state:
        st.session_state.watchlist = {}
    st.session_state.watchlist[symbol] = {"name": name, "sector": sector, "added": datetime.now().strftime("%b %d")}

def remove_from_watchlist(symbol):
    if "watchlist" in st.session_state and symbol in st.session_state.watchlist:
        del st.session_state.watchlist[symbol]

def conviction_color(score):
    if score >= 8: return "#00C9A0"
    if score >= 6: return "#8FBF30"
    if score >= 4: return "#E8A020"
    return "#E05050"

def market_implied_class(view):
    return {"Overvalued": "mi-over", "Undervalued": "mi-under"}.get(view, "mi-fair")

def make_chart(hist, period_label):
    if hist is None or hist.empty:
        return None
    try:
        closes = hist['Close'].dropna()
        if len(closes) < 2:
            return None
        dates = list(closes.index)
        vals = list(closes)
        color = "#00C9A0" if vals[-1] >= vals[0] else "#E05050"
        fill_color = "rgba(0,201,160,0.08)" if color == "#00C9A0" else "rgba(224,80,80,0.08)"
        trace = Scatter(
            x=dates, y=vals,
            mode='lines',
            line=dict(color=color, width=2),
            fill='tozeroy',
            fillcolor=fill_color,
            hovertemplate='%{x|%b %d}<br>$%{y:.2f}<extra></extra>'
        )
        fig = Figure(data=[trace])
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0,r=0,t=10,b=0), height=180,
            xaxis=dict(showgrid=False, showticklabels=True, tickfont=dict(family='Instrument Mono', size=9, color='#3D4250'), tickformat='%b %d'),
            yaxis=dict(showgrid=True, gridcolor='#2A2D35', tickfont=dict(family='Instrument Mono', size=9, color='#3D4250'), tickprefix='$'),
            showlegend=False,
            hoverlabel=dict(bgcolor='#13151A', bordercolor='#2A2D35', font=dict(family='Instrument Mono', size=11, color='#F0F2F5')),
        )
        return fig
    except Exception:
        return None

def sentiment_color(s):
    return {"BULLISH": "#00C9A0", "BEARISH": "#E05050"}.get(s, "#E8A020")

def badge_class(s):
    return {"BULLISH": "", "BEARISH": "badge-bear"}.get(s, "badge-neutral")

def earnings_countdown(next_earnings):
    if next_earnings is None:
        return None, None
    try:
        now = datetime.now()
        ne = next_earnings.replace(tzinfo=None) if hasattr(next_earnings, 'tzinfo') and next_earnings.tzinfo else next_earnings
        delta = (ne - now).days
        return max(0, delta), ne.strftime("%b %d, %Y")
    except:
        return None, None

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div style="font-family:Familjen Grotesk,sans-serif;font-size:1rem;font-weight:700;color:#F0F2F5">NorthBrief</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-hint">AI equity research for Canadian retail investors.</div>', unsafe_allow_html=True)
    st.markdown('<hr style="border:none;border-top:1px solid #2A2D35;margin:1rem 0">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-lbl">Anthropic API Key</div>', unsafe_allow_html=True)
    api_key = st.text_input("key", type="password", placeholder="sk-ant-...", label_visibility="collapsed")
    st.markdown('<div class="sidebar-hint">console.anthropic.com<br>~$0.002 per brief</div>', unsafe_allow_html=True)
    st.markdown('<hr style="border:none;border-top:1px solid #2A2D35;margin:1rem 0">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-lbl">Mode</div>', unsafe_allow_html=True)
    mode = st.radio("mode", ["Single Stock", "Portfolio", "Watchlist"], label_visibility="collapsed")

    st.markdown('<hr style="border:none;border-top:1px solid #2A2D35;margin:1rem 0">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-lbl">AI Analyst Chat</div>', unsafe_allow_html=True)
    if st.button("💬 Ask the Analyst", key="chat_toggle"):
        st.session_state.chat_open = not st.session_state.chat_open
    st.markdown('<div class="sidebar-hint">Ask anything about the current stock or your portfolio.</div>', unsafe_allow_html=True)

    # Init session state
    if "watchlist" not in st.session_state:
        st.session_state.watchlist = {}

# ── NAV ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="nb-nav">
  <div class="nb-logo"><div class="nb-hex"></div><span class="nb-wordmark">NorthBrief</span></div>
  <div class="nb-live"><div class="live-dot"></div><span>Live Data</span></div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SINGLE STOCK MODE
# ══════════════════════════════════════════════════════════════════════════════
if mode == "Single Stock":

    # Session state init
    if "brief_generated" not in st.session_state:
        st.session_state.brief_generated = False
    if "auto_generate" not in st.session_state:
        st.session_state.auto_generate = False
    if "ticker_prefill" not in st.session_state:
        st.session_state.ticker_prefill = ""

    # Input row
    with st.container():
        c1, c2, c3 = st.columns([3,1,6])
        with c1:
            st.markdown('<div style="padding:1rem 0 0 2rem"><div class="sidebar-lbl" style="margin-bottom:6px">Ticker Symbol</div></div>', unsafe_allow_html=True)
            st.markdown('<div style="padding-left:2rem">', unsafe_allow_html=True)
            ticker_input = st.text_input("t", value=st.session_state.ticker_prefill, placeholder="SHOP.TO · CNQ.TO · AAPL", label_visibility="collapsed", key="ticker_main")
            st.markdown('</div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div style="padding-top:3.2rem">', unsafe_allow_html=True)
            go = st.button("Generate →", key="generate_btn")
            st.markdown('</div>', unsafe_allow_html=True)

    # ── EMPTY STATE ───────────────────────────────────────────────────────────
    if not st.session_state.brief_generated and not go:
        st.markdown("""
        <style>
        .empty-wrap { padding: 2.5rem 2rem; max-width: 760px; }
        .empty-hero { font-family: 'Familjen Grotesk', sans-serif; font-size: 1.6rem;
            font-weight: 700; color: #F0F2F5; line-height: 1.3; margin-bottom: 0.5rem; }
        .empty-sub { font-family: 'Instrument Mono', monospace; font-size: 0.7rem;
            letter-spacing: 0.1em; color: #3D4250; text-transform: uppercase; margin-bottom: 2rem; }
        .empty-section-lbl { font-family: 'Instrument Mono', monospace; font-size: 0.57rem;
            letter-spacing: 0.18em; text-transform: uppercase; color: #3D4250; margin-bottom: 0.8rem; }
        .sample-chips { display: flex; gap: 0.6rem; flex-wrap: wrap; margin-bottom: 2rem; }
        .prompt-list { list-style: none; padding: 0; margin: 0; }
        .prompt-list li { font-family: 'Instrument Mono', monospace; font-size: 0.72rem;
            color: #8A8F9E; padding: 0.5rem 0; border-bottom: 1px solid #2A2D35;
            display: flex; align-items: center; gap: 8px; }
        .prompt-list li:last-child { border-bottom: none; }
        .prompt-arrow { color: #00C9A0; }
        .how-grid { display: grid; grid-template-columns: repeat(3,1fr); gap: 1rem; margin-bottom: 2rem; }
        .how-card { background: #13151A; border: 1px solid #2A2D35; border-radius: 8px; padding: 1rem 1.2rem; }
        .how-num { font-family: 'Instrument Mono', monospace; font-size: 0.6rem;
            color: #00C9A0; letter-spacing: 0.14em; margin-bottom: 6px; }
        .how-title { font-size: 0.88rem; font-weight: 700; color: #F0F2F5; margin-bottom: 4px; }
        .how-desc { font-size: 0.78rem; color: #3D4250; line-height: 1.5; }
        </style>
        <div class="empty-wrap">
            <div class="empty-hero">Understand any TSX stock<br>in 10 seconds — not 1 hour.</div>
            <div class="empty-sub">Live data · AI analysis · Canadian market focus</div>
            <div class="how-grid">
                <div class="how-card">
                    <div class="how-num">01</div>
                    <div class="how-title">Key financials summarised</div>
                    <div class="how-desc">P/E, margins, growth, 52W range — pulled live and laid out clearly.</div>
                </div>
                <div class="how-card">
                    <div class="how-num">02</div>
                    <div class="how-title">Bull & bear cases</div>
                    <div class="how-desc">Grounded in actual data. Not generic takes — specific to this stock right now.</div>
                </div>
                <div class="how-card">
                    <div class="how-num">03</div>
                    <div class="how-title">Tracks changes over time</div>
                    <div class="how-desc">Run it again next week. See what shifted and why the view changed.</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Sample ticker buttons
        st.markdown('<div style="padding: 0 2rem"><div class="empty-section-lbl">Try a sample stock</div></div>', unsafe_allow_html=True)
        sc1, sc2, sc3, sc4, sc5 = st.columns([1,1,1,1,6])
        with sc1:
            if st.button("SHOP.TO", key="s1"):
                st.session_state.ticker_prefill = "SHOP.TO"
                st.session_state.auto_generate = True
                st.rerun()
        with sc2:
            if st.button("CSU.TO", key="s2"):
                st.session_state.ticker_prefill = "CSU.TO"
                st.session_state.auto_generate = True
                st.rerun()
        with sc3:
            if st.button("CNQ.TO", key="s3"):
                st.session_state.ticker_prefill = "CNQ.TO"
                st.session_state.auto_generate = True
                st.rerun()
        with sc4:
            if st.button("ATD.TO", key="s4"):
                st.session_state.ticker_prefill = "ATD.TO"
                st.session_state.auto_generate = True
                st.rerun()

        # Example prompts
        st.markdown("""
        <div style="padding: 1.5rem 2rem 0">
            <div class="empty-section-lbl">Try asking the AI analyst</div>
            <ul class="prompt-list">
                <li><span class="prompt-arrow">→</span> Why did CNQ drop recently?</li>
                <li><span class="prompt-arrow">→</span> Is Shopify overvalued right now?</li>
                <li><span class="prompt-arrow">→</span> What are the biggest risks for CSU?</li>
                <li><span class="prompt-arrow">→</span> Compare CNQ and SU as energy picks</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    # ── GENERATION ────────────────────────────────────────────────────────────
    should_generate = go or st.session_state.get("auto_generate", False)
    active_ticker = (ticker_input or st.session_state.ticker_prefill).strip().upper()

    if should_generate and active_ticker:
        if not api_key:
            st.error("Add your Anthropic API key in the sidebar.")
            st.stop()

        ticker = active_ticker
        st.session_state.auto_generate = False
        st.session_state.ticker_prefill = ticker

        with st.spinner(f"Fetching {ticker}..."):
            try:
                d = fetch_data(ticker)
            except Exception as e:
                st.error(f"Could not fetch {ticker}. Check the symbol. `{e}`")
                st.stop()

        with st.spinner("Writing brief..."):
            try:
                prev_snap = get_prev_snapshot(ticker)
                brief = call_claude(build_brief_prompt(d, prev_snap), api_key)
                st.session_state.last_brief = brief
                st.session_state.last_data = d
                st.session_state.brief_generated = True
                save_snapshot(ticker, d, brief)
                st.session_state[f"wl_brief_{ticker}"] = brief
                st.session_state[f"wl_data_{ticker}"] = d
            except Exception as e:
                st.error(f"Brief failed: `{e}`")
                st.stop()

        # ── TICKER BAND ───────────────────────────────────────────────────────
        price = d['price'] or 0
        prev  = d['prev_close'] or price
        chg   = price - prev
        chg_p = (chg/prev*100) if prev else 0
        sign  = "+" if chg >= 0 else ""
        sent  = brief.get("sentiment","NEUTRAL")
        bc    = badge_class(sent)
        meta  = " · ".join(p for p in [d['symbol'], d['exchange'], d['sector']] if p)

        st.markdown(f"""
        <div class="ticker-band">
          <div>
            <div class="tb-name">{d['name']} <span class="badge {bc}">{sent}</span></div>
            <div class="tb-meta">{meta}</div>
          </div>
          <div style="display:flex;align-items:baseline;gap:10px">
            <span class="tb-price">{fmt_p(price)}</span>
            <span class="tb-chg">{sign}{chg:.2f} ({sign}{chg_p:.2f}%)</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # ── STATS STRIP ───────────────────────────────────────────────────────
        st.markdown(f"""
        <div class="stats-strip">
          <div class="smet"><div class="smlbl">Mkt Cap</div><div class="smval">{fmt_cap(d['mkt_cap'])}</div></div>
          <div class="smet"><div class="smlbl">P/E Trail</div><div class="smval">{fmt_x(d['pe'])}</div></div>
          <div class="smet"><div class="smlbl">P/E Fwd</div><div class="smval">{fmt_x(d['fpe'])}</div></div>
          <div class="smet"><div class="smlbl">Rev Growth</div><div class="smval">{fmt_pct(d['rev_growth'])}</div></div>
          <div class="smet"><div class="smlbl">Gross Mgn</div><div class="smval">{fmt_pct(d['gross_margin'])}</div></div>
          <div class="smet"><div class="smlbl">Analyst Tgt</div><div class="smval">{fmt_p(d['target'])}</div></div>
        </div>
        """, unsafe_allow_html=True)

        # ── TABS ─────────────────────────────────────────────────────────────
        tab1, tab2, tab3 = st.tabs(["Brief", "Chart & Technicals", "Peers & History"])

        # ── TAB 1: BRIEF ─────────────────────────────────────────────────────
        with tab1:
            st.markdown('<div class="nb-content">', unsafe_allow_html=True)

            # What Changed banner
            prev_snap = get_prev_snapshot(ticker)
            what_changed_txt = brief.get('what_changed', 'First analysis for this ticker.')
            if prev_snap and 'First analysis' not in what_changed_txt:
                prev_pos = prev_snap.get('positioning','—')
                curr_pos = brief.get('positioning','—')
                st.markdown(f"""
                <div class="wc-card">
                  <div class="slbl" style="color:#8FBF30;margin-bottom:8px">What Changed</div>
                  <div class="wc-shift">
                    <span class="wc-pill wc-from">{prev_pos}</span>
                    <span class="wc-arrow"> → </span>
                    <span class="wc-pill wc-to">{curr_pos}</span>
                  </div>
                  <div class="sbody">{what_changed_txt}</div>
                </div>
                """, unsafe_allow_html=True)

            # Conviction + Analyst Positioning block
            conv = brief.get('conviction', 5)
            try: conv = int(conv)
            except: conv = 5
            conv = max(1, min(10, conv))
            conv_color = conviction_color(conv)
            positioning = brief.get('positioning', sent.capitalize())
            miv = brief.get('market_implied_view', 'Fair Value')
            mi_class = market_implied_class(miv)

            st.markdown(f"""
            <div class="dyn-card" style="margin-bottom:1rem">
              <div style="display:flex;align-items:flex-start;justify-content:space-between">
                <div style="display:flex;align-items:center;gap:1.2rem">
                  <div>
                    <span class="conviction-score" style="color:{conv_color}">{conv}</span>
                    <span class="conviction-score-denom">/10</span>
                  </div>
                  <div>
                    <div class="conviction-label">{positioning}</div>
                    <div class="conviction-rationale">{brief.get('conviction_rationale','—')}</div>
                    <div class="market-implied {mi_class}">{miv}</div>
                  </div>
                </div>
                <div style="text-align:right;padding-top:4px">
                  <div class="dyn-lbl" style="margin-bottom:6px">Conviction</div>
                  <div class="conviction-bar-track" style="width:120px">
                    <div class="conviction-bar-fill" style="width:{conv*10}%;background:{conv_color}"></div>
                  </div>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)

            # Add to watchlist
            in_wl = "watchlist" in st.session_state and ticker in st.session_state.get("watchlist", {})
            wl_col1, wl_col2 = st.columns([3, 7])
            with wl_col1:
                if not in_wl:
                    if st.button(f"+ Add {ticker} to Watchlist", key="add_wl"):
                        add_to_watchlist(ticker, d['name'], d['sector'])
                        st.rerun()
                else:
                    if st.button(f"✓ In Watchlist — Remove", key="rm_wl"):
                        remove_from_watchlist(ticker)
                        st.rerun()

            # Dynamic row
            h52, l52 = d['52h'] or 0, d['52l'] or 0
            rng_pct = int(((price - l52)/(h52 - l52))*100) if h52 != l52 else 50
            from_low_pct = round(((price - l52)/l52)*100, 1) if l52 else 0
            upside = round(((d['target'] or price) - price)/price*100, 1) if price else 0
            upside_sign = "+" if upside >= 0 else ""
            upside_cls = "neg" if upside < 0 else ""
            sc = sentiment_color(sent)

            bar_html = ""
            levels = [2,3,4,5,6,7,8,7,5,3] if sent=="BULLISH" else [8,7,5,4,3,2,2,2,2,1] if sent=="BEARISH" else [3,4,5,6,7,7,6,5,4,3]
            for i, lv in enumerate(levels):
                h_px = int((lv/8)*44)
                active = (i >= 5 and sent=="BULLISH") or (i <= 4 and sent=="BEARISH") or sent=="NEUTRAL"
                col = sc if active else "#2A2D35"
                bar_html += f'<div style="width:13px;height:{h_px}px;background:{col};border-radius:2px 2px 0 0;flex-shrink:0"></div>'

            days_to_earnings, earnings_date_str = earnings_countdown(d.get('next_earnings'))

            st.markdown(f"""
            <div class="dyn-row">
              <div class="dyn-card">
                <div class="dyn-lbl">52-Week Range</div>
                <div class="range-track">
                  <div class="range-fill" style="width:{rng_pct}%"></div>
                  <div class="range-thumb" style="left:{rng_pct}%"></div>
                </div>
                <div class="range-labels"><span class="rlbl">{fmt_p(l52)}</span><span class="rlbl">{fmt_p(h52)}</span></div>
                <div class="range-current">{fmt_p(price)}</div>
                <div class="range-pct">+{from_low_pct}% from 52W low</div>
              </div>
              <div class="dyn-card">
                <div class="dyn-lbl">Upside to Target</div>
                <div class="upside-num {upside_cls}">{upside_sign}{upside}%</div>
                <div class="upside-sub">{'upside' if upside >= 0 else 'downside'} to analyst target</div>
                <div class="upside-detail">
                  <div><div class="ud-lbl">Current</div><div class="ud-val">{fmt_p(price)}</div></div>
                  <div><div class="ud-lbl">Target</div><div class="ud-val">{fmt_p(d['target'])}</div></div>
                  <div><div class="ud-lbl">Consensus</div><div class="ud-val" style="color:{'#00C9A0' if 'BUY' in d['rec'] else '#E05050' if 'SELL' in d['rec'] else '#E8A020'}">{d['rec'] or '—'}</div></div>
                </div>
              </div>
              <div class="dyn-card">
                <div class="dyn-lbl">Sentiment Signal</div>
                <div style="display:flex;align-items:flex-end;gap:3px;height:44px;margin-bottom:6px">{bar_html}</div>
                <div class="gauge-lbl" style="color:{sc}">{sent.capitalize()}</div>
                <div class="gauge-sub">Based on AI analysis</div>
              </div>
            </div>
            """, unsafe_allow_html=True)

            # Earnings countdown
            if days_to_earnings is not None:
                ec_color = "#E8A020" if days_to_earnings <= 14 else "#00C9A0"
                st.markdown(f"""
                <div class="dyn-card" style="margin-bottom:1rem;display:flex;align-items:center;justify-content:space-between">
                  <div class="dyn-lbl" style="margin-bottom:0">Next Earnings</div>
                  <div style="text-align:right">
                    <span style="font-family:'Instrument Mono',monospace;font-size:1.6rem;font-weight:700;color:{ec_color}">{days_to_earnings}</span>
                    <span style="font-family:'Instrument Mono',monospace;font-size:0.65rem;color:#3D4250"> days · {earnings_date_str}</span>
                    {'<span style="font-family:Instrument Mono,monospace;font-size:0.52rem;letter-spacing:0.12em;text-transform:uppercase;padding:3px 10px;border-radius:20px;background:#2A1A00;color:#E8A020;margin-left:8px">Earnings Soon</span>' if days_to_earnings <= 14 else ''}
                  </div>
                </div>
                """, unsafe_allow_html=True)

            # Why it moved
            st.markdown(f"""
            <div class="move-card" style="margin-bottom:1rem">
              <div class="slbl l-move">Why It Moved</div>
              <div class="sbody">{brief.get('why_moved','—')}</div>
            </div>
            """, unsafe_allow_html=True)

            # Upside / Downside drivers
            up_drivers = brief.get('upside_drivers', [])
            dn_drivers = brief.get('downside_drivers', [])
            up_html = "".join([f'<div class="driver-item"><div class="driver-dot" style="background:#00C9A0"></div><div class="driver-txt">{drv}</div></div>' for drv in up_drivers])
            dn_html = "".join([f'<div class="driver-item"><div class="driver-dot" style="background:#E05050"></div><div class="driver-txt">{drv}</div></div>' for drv in dn_drivers])
            st.markdown(f"""
            <div class="drivers-grid">
              <div class="driver-card">
                <div class="slbl l-bull" style="margin-bottom:0.6rem">Upside Drivers</div>
                {up_html}
              </div>
              <div class="driver-card">
                <div class="slbl l-bear" style="margin-bottom:0.6rem">Downside Drivers</div>
                {dn_html}
              </div>
            </div>
            """, unsafe_allow_html=True)

            # Core brief
            st.markdown(f"""
            <div class="overview-card">
              <div class="slbl l-snap">Overview</div>
              <div class="sbody">{brief['summary']}</div>
            </div>
            <div class="cards-grid">
              <div class="card card-bull"><div class="slbl l-bull">Bull Case</div><div class="sbody">{brief['bull_case']}</div></div>
              <div class="card card-bear"><div class="slbl l-bear">Bear Case</div><div class="sbody">{brief['bear_case']}</div></div>
            </div>
            <div class="verdict-card">
              <div class="slbl l-verdict">Verdict</div>
              <div class="sbody-verdict">{brief['verdict']}</div>
              <div class="krisk">KEY RISK — <span>{brief['key_risk']}</span></div>
            </div>
            """, unsafe_allow_html=True)

            # What Would Change This View
            st.markdown(f"""
            <div class="wtc-card">
              <div class="slbl" style="color:var(--amber);margin-bottom:8px">What Would Change This View</div>
              <div class="sbody">{brief.get('what_would_change','—')}</div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)

        # ── TAB 2: CHART ─────────────────────────────────────────────────────
        with tab2:
            st.markdown('<div class="nb-content">', unsafe_allow_html=True)
            period = st.radio("Period", ["7D", "1M", "1Y"], horizontal=True)
            hist_map = {"7D": d['hist_1w'], "1M": d['hist_1m'], "1Y": d['hist_1y']}
            fig = make_chart(hist_map[period], period)
            if fig:
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

            # Technical metrics
            h = d['hist_1y']
            if not h.empty:
                closes = h['Close'].dropna()
                ma20  = closes.rolling(20).mean().iloc[-1]
                ma50  = closes.rolling(50).mean().iloc[-1]
                vol   = closes.pct_change().std() * (252**0.5) * 100
                st.markdown(f"""
                <div class="stats-strip" style="grid-template-columns:repeat(5,1fr);border-top:1px solid #2A2D35;border-bottom:none;border-radius:8px">
                  <div class="smet"><div class="smlbl">20D MA</div><div class="smval">${ma20:.2f}</div></div>
                  <div class="smet"><div class="smlbl">50D MA</div><div class="smval">${ma50:.2f}</div></div>
                  <div class="smet"><div class="smlbl">vs 20D MA</div><div class="smval" style="color:{'#00C9A0' if price > ma20 else '#E05050'}">{'+' if price > ma20 else ''}{((price-ma20)/ma20*100):.1f}%</div></div>
                  <div class="smet"><div class="smlbl">Annl. Vol</div><div class="smval">{vol:.1f}%</div></div>
                  <div class="smet"><div class="smlbl">Beta</div><div class="smval">{f"{d['beta']:.2f}" if d['beta'] else '—'}</div></div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # ── TAB 3: PEERS & HISTORY ────────────────────────────────────────────
        with tab3:
            st.markdown('<div class="nb-content">', unsafe_allow_html=True)
            st.markdown('<div class="section-hdr">Sector Peer Comparison</div>', unsafe_allow_html=True)

            # Peer context from AI
            st.markdown(f"""
            <div class="card" style="margin-bottom:1rem;border-left:3px solid #E8A020">
              <div class="slbl l-peer">Peer Context</div>
              <div class="sbody">{brief.get('peer_context','—')}</div>
            </div>
            """, unsafe_allow_html=True)

            # Peer data table
            peers = get_peers(d['sector'], d['exchange'], d['symbol'])
            if peers:
                with st.spinner("Loading peer data..."):
                    peer_rows = []
                    for p in peers:
                        try:
                            pi = yf.Ticker(p).info
                            peer_rows.append({
                                "ticker": p,
                                "pe": pi.get("trailingPE"),
                                "fpe": pi.get("forwardPE"),
                                "rev_growth": pi.get("revenueGrowth"),
                                "gross_margin": pi.get("grossMargins"),
                                "mkt_cap": pi.get("marketCap"),
                            })
                        except: pass

                rows_html = ""
                for pr in peer_rows:
                    rows_html += f"""<tr>
                      <td>{pr['ticker']}</td>
                      <td>{fmt_x(pr['pe'])}</td>
                      <td>{fmt_x(pr['fpe'])}</td>
                      <td>{fmt_pct(pr['rev_growth'])}</td>
                      <td>{fmt_pct(pr['gross_margin'])}</td>
                      <td>{fmt_cap(pr['mkt_cap'])}</td>
                    </tr>"""
                # Current stock highlighted
                curr_row = f"""<tr class="highlight">
                  <td>{d['symbol']} ★</td>
                  <td>{fmt_x(d['pe'])}</td>
                  <td>{fmt_x(d['fpe'])}</td>
                  <td>{fmt_pct(d['rev_growth'])}</td>
                  <td>{fmt_pct(d['gross_margin'])}</td>
                  <td>{fmt_cap(d['mkt_cap'])}</td>
                </tr>"""

                st.markdown(f"""
                <table class="peer-table">
                  <thead><tr>
                    <th>Ticker</th><th>P/E</th><th>Fwd P/E</th>
                    <th>Rev Growth</th><th>Gross Mgn</th><th>Mkt Cap</th>
                  </tr></thead>
                  <tbody>{curr_row}{rows_html}</tbody>
                </table>
                """, unsafe_allow_html=True)

            # Sentiment history
            st.markdown('<div class="section-hdr" style="margin-top:2rem">Bull/Bear Signal History</div>', unsafe_allow_html=True)

            hist_key = f"history_{ticker}"
            if hist_key not in st.session_state:
                st.session_state[hist_key] = []

            entry = {
                "date": datetime.now().strftime("%b %d, %H:%M"),
                "sentiment": sent,
                "snippet": brief['verdict'][:80] + "..."
            }
            existing = st.session_state[hist_key]
            if not existing or existing[-1]['date'] != entry['date']:
                existing.append(entry)
            st.session_state[hist_key] = existing[-8:]

            history_html = ""
            for h in reversed(st.session_state[hist_key]):
                sc2 = sentiment_color(h['sentiment'])
                history_html += f"""
                <div class="history-row">
                  <span class="hist-date">{h['date']}</span>
                  <div class="hist-dot" style="background:{sc2}"></div>
                  <span class="hist-label" style="color:{sc2};width:60px">{h['sentiment'].capitalize()}</span>
                  <span class="hist-snippet">{h['snippet']}</span>
                </div>"""

            st.markdown(f'<div class="dyn-card">{history_html}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PORTFOLIO MODE
# ══════════════════════════════════════════════════════════════════════════════
elif mode == "Portfolio":
    st.markdown('<div style="padding:1rem 2rem 0">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-lbl" style="margin-bottom:6px">Enter up to 5 tickers (comma separated)</div>', unsafe_allow_html=True)
    c1, c2 = st.columns([4,1])
    with c1:
        port_input = st.text_input("p", placeholder="SHOP.TO, CNQ.TO, RY.TO, ATD.TO", label_visibility="collapsed")
    with c2:
        port_go = st.button("Analyse Portfolio →")
    st.markdown('</div>', unsafe_allow_html=True)

    if port_go and port_input:
        if not api_key:
            st.error("Add your Anthropic API key in the sidebar.")
            st.stop()

        tickers = [t.strip().upper() for t in port_input.split(",") if t.strip()][:5]
        port_data = {}

        with st.spinner("Fetching portfolio data..."):
            for t in tickers:
                try:
                    port_data[t] = fetch_data(t)
                except:
                    st.warning(f"Could not fetch {t} — skipping.")

        if not port_data:
            st.error("No valid tickers found.")
            st.stop()

        with st.spinner("Analysing portfolio..."):
            try:
                port_briefs = {}
                for sym, d in port_data.items():
                    b = call_claude(build_brief_prompt(d), api_key)
                    port_briefs[sym] = b
                port_analysis = call_claude(build_portfolio_prompt(port_data), api_key)
                st.session_state.port_data = port_data
                st.session_state.port_briefs = port_briefs
            except Exception as e:
                st.error(f"Analysis failed: `{e}`")
                st.stop()

        overall_sent = port_analysis.get("overall_sentiment","NEUTRAL")
        oc = sentiment_color(overall_sent)

        st.markdown(f"""
        <div class="ticker-band">
          <div>
            <div class="tb-name">Portfolio Analysis <span class="badge {badge_class(overall_sent)}">{overall_sent}</span></div>
            <div class="tb-meta">{len(port_data)} Holdings · {datetime.now().strftime('%b %d, %Y')}</div>
          </div>
          <div style="text-align:right">
            <div style="font-family:'Instrument Mono',monospace;font-size:0.7rem;color:{oc}">{port_analysis.get('best_positioned','—')} Best Positioned</div>
            <div style="font-family:'Instrument Mono',monospace;font-size:0.7rem;color:#E05050;margin-top:4px">{port_analysis.get('most_exposed','—')} Most Exposed</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="nb-content">', unsafe_allow_html=True)

        # Portfolio summary cards
        st.markdown(f"""
        <div class="cards-grid" style="margin-bottom:1rem">
          <div class="overview-card" style="margin-bottom:0">
            <div class="slbl l-snap">Portfolio Overview</div>
            <div class="sbody">{port_analysis.get('summary','—')}</div>
          </div>
          <div class="overview-card" style="margin-bottom:0;border-left-color:#E05050">
            <div class="slbl l-bear">Biggest Risk</div>
            <div class="sbody">{port_analysis.get('biggest_risk','—')}</div>
          </div>
        </div>
        <div class="move-card" style="margin-bottom:1rem">
          <div class="slbl l-move">Diversification Assessment</div>
          <div class="sbody">{port_analysis.get('diversification','—')}</div>
        </div>
        """, unsafe_allow_html=True)

        # Holdings table
        st.markdown('<div class="section-hdr">Holdings Breakdown</div>', unsafe_allow_html=True)
        header = """<div class="port-row port-header" style="border-bottom:1px solid #2A2D35">
          <div style="font-family:'Instrument Mono',monospace;font-size:0.5rem;letter-spacing:0.12em;text-transform:uppercase;color:#3D4250">Stock</div>
          <div style="font-family:'Instrument Mono',monospace;font-size:0.5rem;letter-spacing:0.12em;text-transform:uppercase;color:#3D4250;text-align:right">P/E</div>
          <div style="font-family:'Instrument Mono',monospace;font-size:0.5rem;letter-spacing:0.12em;text-transform:uppercase;color:#3D4250;text-align:right">1Y Ret</div>
          <div style="font-family:'Instrument Mono',monospace;font-size:0.5rem;letter-spacing:0.12em;text-transform:uppercase;color:#3D4250;text-align:right">Target</div>
          <div style="font-family:'Instrument Mono',monospace;font-size:0.5rem;letter-spacing:0.12em;text-transform:uppercase;color:#3D4250;text-align:right">Signal</div>
        </div>"""

        rows_html = header
        for sym, d in port_data.items():
            b = port_briefs.get(sym, {})
            s = b.get("sentiment","NEUTRAL")
            sc2 = sentiment_color(s)
            ret = d.get('price_1y')
            ret_str = fmt_pct(ret) if ret else "—"
            ret_color = "#00C9A0" if (ret and ret > 0) else "#E05050"
            rows_html += f"""<div class="port-row">
              <div>
                <div class="port-ticker">{sym}</div>
                <div class="port-name">{d['name'][:22]}</div>
              </div>
              <div class="port-val">{fmt_x(d['pe'])}</div>
              <div class="port-val" style="color:{ret_color}">{ret_str}</div>
              <div class="port-val">{fmt_p(d['target'])}</div>
              <div style="text-align:right"><span class="port-badge" style="background:{'#003D31' if s=='BULLISH' else '#3D1515' if s=='BEARISH' else '#2A1A00'};color:{sc2}">{s.capitalize()}</span></div>
            </div>"""

        st.markdown(f'<div class="dyn-card">{rows_html}</div>', unsafe_allow_html=True)

        # Individual briefs
        st.markdown('<div class="section-hdr" style="margin-top:2rem">Individual Stock Verdicts</div>', unsafe_allow_html=True)
        for sym, b in port_briefs.items():
            s = b.get("sentiment","NEUTRAL")
            sc2 = sentiment_color(s)
            st.markdown(f"""
            <div class="dyn-card" style="margin-bottom:0.8rem;border-left:3px solid {sc2}">
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
                <div class="slbl" style="color:{sc2};margin-bottom:0">{sym}</div>
                <span style="font-family:'Instrument Mono',monospace;font-size:0.52rem;letter-spacing:0.12em;text-transform:uppercase;padding:2px 8px;border-radius:20px;background:{'#003D31' if s=='BULLISH' else '#3D1515' if s=='BEARISH' else '#2A1A00'};color:{sc2}">{s.capitalize()}</span>
              </div>
              <div class="sbody">{b.get('verdict','—')}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# WATCHLIST MODE
# ══════════════════════════════════════════════════════════════════════════════
elif mode == "Watchlist":
    st.markdown("""
    <div class="ticker-band">
      <div>
        <div class="tb-name">My Watchlist</div>
        <div class="tb-meta">Tracked Stocks · Session Data</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="nb-content">', unsafe_allow_html=True)

    watchlist = st.session_state.get("watchlist", {})

    if not watchlist:
        st.markdown("""
        <div class="dyn-card">
          <div class="wl-empty">No stocks in your watchlist yet.<br>Generate a brief and click "+ Add to Watchlist" to save stocks here.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Refresh all button
        refresh_col1, refresh_col2 = st.columns([2, 8])
        with refresh_col1:
            refresh_all = st.button("↻ Refresh All Briefs", key="refresh_wl")

        if refresh_all and api_key:
            with st.spinner("Refreshing watchlist..."):
                for sym in list(watchlist.keys()):
                    try:
                        wd = fetch_data(sym)
                        prev = get_prev_snapshot(sym)
                        wb = call_claude(build_brief_prompt(wd, prev), api_key)
                        save_snapshot(sym, wd, wb)
                        st.session_state[f"wl_brief_{sym}"] = wb
                        st.session_state[f"wl_data_{sym}"] = wd
                    except:
                        pass
            st.success("Watchlist refreshed.")

        # Watchlist table header
        header_html = """
        <div class="wl-row" style="border-bottom:2px solid #2A2D35">
          <div style="font-family:'Instrument Mono',monospace;font-size:0.5rem;letter-spacing:0.12em;text-transform:uppercase;color:#3D4250">Stock</div>
          <div style="font-family:'Instrument Mono',monospace;font-size:0.5rem;letter-spacing:0.12em;text-transform:uppercase;color:#3D4250;text-align:right">Price</div>
          <div style="font-family:'Instrument Mono',monospace;font-size:0.5rem;letter-spacing:0.12em;text-transform:uppercase;color:#3D4250;text-align:right">Conviction</div>
          <div style="font-family:'Instrument Mono',monospace;font-size:0.5rem;letter-spacing:0.12em;text-transform:uppercase;color:#3D4250;text-align:right">Positioning</div>
          <div style="font-family:'Instrument Mono',monospace;font-size:0.5rem;letter-spacing:0.12em;text-transform:uppercase;color:#3D4250;text-align:right">Signal</div>
          <div></div>
        </div>"""

        rows_html = header_html
        for sym, meta in watchlist.items():
            wb = st.session_state.get(f"wl_brief_{sym}") or st.session_state.get(f"snapshot_{sym}", [{}])[-1] if st.session_state.get(f"snapshot_{sym}") else None
            wd = st.session_state.get(f"wl_data_{sym}")

            price_str = fmt_p(wd['price']) if wd else "—"
            conv_str = f"{wb.get('conviction','—')}/10" if wb else "—"
            pos_str = wb.get('positioning', wb.get('sentiment','—').capitalize()) if wb else "—"
            s = wb.get('sentiment','NEUTRAL') if wb else 'NEUTRAL'
            sc2 = sentiment_color(s)
            conv_val = wb.get('conviction', 5) if wb else 5
            try: conv_val = int(conv_val)
            except: conv_val = 5
            cc = conviction_color(conv_val)

            rows_html += f"""
            <div class="wl-row">
              <div>
                <div class="wl-ticker">{sym}</div>
                <div class="wl-name">{meta.get('name','')[:22]}</div>
              </div>
              <div class="wl-val">{price_str}</div>
              <div class="wl-val" style="color:{cc}">{conv_str}</div>
              <div class="wl-val" style="font-size:0.68rem;color:{sc2}">{pos_str}</div>
              <div style="text-align:right"><span class="wl-badge" style="background:{'#003D31' if s=='BULLISH' else '#3D1515' if s=='BEARISH' else '#2A1A00'};color:{sc2}">{s.capitalize()}</span></div>
              <div class="wl-val">—</div>
            </div>"""

        st.markdown(f'<div class="dyn-card">{rows_html}</div>', unsafe_allow_html=True)

        # Individual watchlist briefs
        st.markdown('<div class="section-hdr" style="margin-top:2rem">Latest Verdicts</div>', unsafe_allow_html=True)
        for sym in watchlist:
            wb = st.session_state.get(f"wl_brief_{sym}")
            snaps = st.session_state.get(f"snapshot_{sym}", [])
            if snaps:
                last = snaps[-1]
                s = last.get('sentiment','NEUTRAL')
                sc2 = sentiment_color(s)
                pos = last.get('positioning', s.capitalize())
                conv = last.get('conviction', 5)
                try: conv = int(conv)
                except: conv = 5
                cc = conviction_color(conv)
                st.markdown(f"""
                <div class="dyn-card" style="margin-bottom:0.8rem;border-left:3px solid {sc2}">
                  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
                    <div style="display:flex;align-items:center;gap:10px">
                      <div class="wl-ticker">{sym}</div>
                      <span style="font-family:'Instrument Mono',monospace;font-size:0.52rem;letter-spacing:0.1em;text-transform:uppercase;padding:2px 8px;border-radius:20px;background:{'#003D31' if s=='BULLISH' else '#3D1515' if s=='BEARISH' else '#2A1A00'};color:{sc2}">{pos}</span>
                    </div>
                    <div style="font-family:'Instrument Mono',monospace;font-size:0.65rem;color:{cc}">{conv}/10 conviction · {last.get('date','—')}</div>
                  </div>
                  <div class="sbody">{last.get('verdict','Generate a brief to see the verdict.')}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="dyn-card" style="margin-bottom:0.8rem;border-left:3px solid #2A2D35">
                  <div class="wl-ticker" style="margin-bottom:6px">{sym}</div>
                  <div class="sbody" style="color:#3D4250">Generate a brief for this stock to see its verdict here.</div>
                </div>
                """, unsafe_allow_html=True)

        # Remove buttons
        st.markdown('<div class="section-hdr" style="margin-top:1.5rem">Manage Watchlist</div>', unsafe_allow_html=True)
        rm_cols = st.columns(min(len(watchlist), 5))
        for i, sym in enumerate(list(watchlist.keys())):
            with rm_cols[i % 5]:
                if st.button(f"Remove {sym}", key=f"rm_{sym}"):
                    remove_from_watchlist(sym)
                    st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
st.markdown(f"""
<div class="nb-footer">
  <div class="ftxt">NorthBrief · Alpha · Not financial advice</div>
  <div class="fclock">{datetime.now().strftime('%b %d, %Y · %H:%M')}</div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# FLOATING AI ANALYST CHAT
# ══════════════════════════════════════════════════════════════════════════════

st.markdown("""
<style>
.chat-fab {
    position: fixed; bottom: 2rem; right: 2rem; z-index: 9999;
    width: 52px; height: 52px; background: #00C9A0; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    cursor: pointer; box-shadow: 0 4px 20px rgba(0,201,160,0.35);
    transition: transform 0.2s, box-shadow 0.2s;
}
.chat-fab:hover { transform: scale(1.08); box-shadow: 0 6px 28px rgba(0,201,160,0.5); }
.chat-fab svg { width: 22px; height: 22px; fill: #13151A; }
.chat-unread {
    position: absolute; top: -3px; right: -3px; width: 14px; height: 14px;
    background: #E05050; border-radius: 50%; border: 2px solid #1C1F26;
}
.chat-window-header {
    background: #13151A; padding: 1rem 1.2rem;
    border-bottom: 1px solid #2A2D35; border-radius: 12px 12px 0 0;
    display: flex; align-items: center; justify-content: space-between;
}
.chat-header-left { display: flex; align-items: center; gap: 8px; }
.chat-header-title {
    font-family: 'Familjen Grotesk', sans-serif;
    font-size: 0.9rem; font-weight: 700; color: #F0F2F5;
}
.chat-header-sub {
    font-family: 'Instrument Mono', monospace;
    font-size: 0.55rem; letter-spacing: 0.12em;
    color: #3D4250; text-transform: uppercase; margin-top: 1px;
}
.chat-msg-user {
    display: flex; justify-content: flex-end; margin-bottom: 0.8rem;
}
.chat-msg-ai {
    display: flex; justify-content: flex-start; margin-bottom: 0.8rem;
}
.chat-bubble-user {
    background: #00C9A0; color: #13151A;
    font-family: 'DM Sans', 'Familjen Grotesk', sans-serif;
    font-size: 0.84rem; line-height: 1.6;
    padding: 0.65rem 1rem; border-radius: 16px 16px 4px 16px;
    max-width: 80%;
}
.chat-bubble-ai {
    background: #13151A; color: #8A8F9E;
    font-family: 'DM Sans', 'Familjen Grotesk', sans-serif;
    font-size: 0.84rem; line-height: 1.6;
    padding: 0.65rem 1rem; border-radius: 16px 16px 16px 4px;
    max-width: 85%; border: 1px solid #2A2D35;
}
.chat-avatar {
    width: 26px; height: 26px; background: #00C9A0;
    clip-path: polygon(50% 0%,100% 25%,100% 75%,50% 100%,0% 75%,0% 25%);
    flex-shrink: 0; margin-right: 8px; margin-top: 2px;
}
.chat-suggestions {
    display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 0.8rem;
}
.chat-suggestion {
    font-family: 'Instrument Mono', monospace; font-size: 0.58rem;
    letter-spacing: 0.06em; color: #00C9A0; background: #003D31;
    border: 1px solid #00C9A0; border-radius: 20px;
    padding: 4px 12px; cursor: pointer;
}
</style>
""", unsafe_allow_html=True)

# Build system context for the analyst
def build_analyst_context():
    ctx_parts = ["You are NorthBrief's AI analyst — a senior equity research analyst specialising in Canadian and North American stocks. You are concise, direct, and financially literate. You give specific, data-grounded answers. Never give generic advice. Always ground answers in the specific financial data you have been given. If asked to compare stocks, do so using actual metrics. Do not recommend buying or selling — frame everything as analysis, not advice."]

    # Inject current brief context if available
    if 'last_brief' in st.session_state and st.session_state.last_brief:
        d = st.session_state.last_data
        b = st.session_state.last_brief
        ctx_parts.append(f"""
CURRENT STOCK IN FOCUS: {d['name']} ({d['symbol']})
Sector: {d['sector']} | Industry: {d['industry']}
Price: {fmt_p(d['price'])} | Mkt Cap: {fmt_cap(d['mkt_cap'])}
P/E: {fmt_x(d['pe'])} | Fwd P/E: {fmt_x(d['fpe'])} | EV/EBITDA: {fmt_x(d['ev_ebitda'])}
Rev Growth: {fmt_pct(d['rev_growth'])} | Gross Margin: {fmt_pct(d['gross_margin'])}
52W Range: {fmt_p(d['52l'])} – {fmt_p(d['52h'])} | Analyst Target: {fmt_p(d['target'])} | Consensus: {d['rec']}
Beta: {d['beta']} | ROE: {fmt_pct(d['roe'])} | D/E: {d['de']}
AI Brief Summary: {b.get('summary','')}
Bull Case: {b.get('bull_case','')}
Bear Case: {b.get('bear_case','')}
Verdict: {b.get('verdict','')}
Key Risk: {b.get('key_risk','')}
Sentiment: {b.get('sentiment','')}
""")

    # Inject portfolio context if available
    if 'port_data' in st.session_state and st.session_state.port_data:
        ctx_parts.append("PORTFOLIO CONTEXT:")
        for sym, d in st.session_state.port_data.items():
            b = st.session_state.port_briefs.get(sym, {})
            ctx_parts.append(f"  {sym}: {d['sector']}, P/E {fmt_x(d['pe'])}, Rev Growth {fmt_pct(d['rev_growth'])}, 1Y Return {fmt_pct(d['price_1y'])}, Sentiment: {b.get('sentiment','')}, Verdict: {b.get('verdict','')[:100]}")

    return "\n".join(ctx_parts)


def chat_with_analyst(messages, api_key):
    client = anthropic.Anthropic(api_key=api_key)
    system = build_analyst_context()
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=600,
        system=system,
        messages=messages
    )
    return response.content[0].text


# Store context in session state when brief is generated
if 'last_brief' not in st.session_state:
    st.session_state.last_brief = None
    st.session_state.last_data = None
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []
if 'chat_open' not in st.session_state:
    st.session_state.chat_open = False
if 'port_data' not in st.session_state:
    st.session_state.port_data = {}
if 'port_briefs' not in st.session_state:
    st.session_state.port_briefs = {}

# Persist brief/data after generation (inject into session state)
# This runs after the main blocks above have set locals — we re-check
try:
    if 'brief' in dir() and brief and 'd' in dir() and d:
        st.session_state.last_brief = brief
        st.session_state.last_data = d
except:
    pass
try:
    if 'port_data' in dir() and port_data:
        st.session_state.port_data = port_data
    if 'port_briefs' in dir() and port_briefs:
        st.session_state.port_briefs = port_briefs
except:
    pass

# Chat window
if st.session_state.chat_open:
    st.markdown("""
    <div style="position:fixed;bottom:5rem;right:2rem;width:420px;z-index:9998;
        background:#1C1F26;border:1px solid #2A2D35;border-radius:12px;
        box-shadow:0 8px 40px rgba(0,0,0,0.6);">
    """, unsafe_allow_html=True)

    # Header
    context_label = ""
    if st.session_state.last_data:
        context_label = st.session_state.last_data.get('symbol', '')
    elif st.session_state.port_data:
        context_label = "Portfolio"

    st.markdown(f"""
    <div class="chat-window-header">
        <div class="chat-header-left">
            <div style="width:20px;height:20px;background:#00C9A0;
                clip-path:polygon(50% 0%,100% 25%,100% 75%,50% 100%,0% 75%,0% 25%)"></div>
            <div>
                <div class="chat-header-title">AI Analyst</div>
                <div class="chat-header-sub">{"Context: " + context_label if context_label else "No brief loaded yet"}</div>
            </div>
        </div>
        <div style="font-family:'Instrument Mono',monospace;font-size:0.6rem;color:#3D4250">Full analyst mode</div>
    </div>
    """, unsafe_allow_html=True)

    # Suggestions if no messages yet
    if not st.session_state.chat_messages and st.session_state.last_data:
        sym = st.session_state.last_data.get('symbol','')
        suggestions = [
            f"Is {sym} expensive vs peers?",
            "What's the biggest risk right now?",
            "Bull case if they beat earnings?",
            "What drives the stock higher?",
        ]
        st.markdown('<div style="padding:0.8rem 1rem 0"><div class="chat-suggestions">', unsafe_allow_html=True)
        for i, s in enumerate(suggestions):
            if st.button(s, key=f"suggestion_{i}"):
                st.session_state.chat_messages.append({"role": "user", "content": s})
                with st.spinner(""):
                    reply = chat_with_analyst(st.session_state.chat_messages, api_key)
                st.session_state.chat_messages.append({"role": "assistant", "content": reply})
                st.rerun()
        st.markdown('</div></div>', unsafe_allow_html=True)

    # Message history
    msgs_html = '<div style="padding:0.8rem 1rem;max-height:320px;overflow-y:auto;display:flex;flex-direction:column;gap:0">'
    if not st.session_state.chat_messages:
        msgs_html += '<div style="font-family:Instrument Mono,monospace;font-size:0.65rem;color:#3D4250;text-align:center;padding:1rem 0">Generate a brief first, then ask anything about the stock.</div>'
    for msg in st.session_state.chat_messages:
        if msg['role'] == 'user':
            msgs_html += f'<div class="chat-msg-user"><div class="chat-bubble-user">{msg["content"]}</div></div>'
        else:
            msgs_html += f'<div class="chat-msg-ai"><div class="chat-avatar"></div><div class="chat-bubble-ai">{msg["content"]}</div></div>'
    msgs_html += '</div>'
    st.markdown(msgs_html, unsafe_allow_html=True)

    # Input row
    st.markdown('<div style="padding:0.6rem 1rem;border-top:1px solid #2A2D35">', unsafe_allow_html=True)
    chat_col1, chat_col2 = st.columns([5, 1])
    with chat_col1:
        user_input = st.text_input("msg", placeholder="Ask anything about this stock...", label_visibility="collapsed", key="chat_input")
    with chat_col2:
        send = st.button("→", key="chat_send")

    if send and user_input and api_key:
        st.session_state.chat_messages.append({"role": "user", "content": user_input})
        with st.spinner(""):
            reply = chat_with_analyst(st.session_state.chat_messages, api_key)
        st.session_state.chat_messages.append({"role": "assistant", "content": reply})
        st.rerun()
    elif send and not api_key:
        st.error("Add your API key in the sidebar.")

    # Clear button
    if st.session_state.chat_messages:
        if st.button("Clear chat", key="chat_clear"):
            st.session_state.chat_messages = []
            st.rerun()

    st.markdown('</div></div>', unsafe_allow_html=True)
