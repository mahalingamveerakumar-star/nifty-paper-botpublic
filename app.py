
import streamlit as st
import sqlite3
from datetime import datetime, time
from zoneinfo import ZoneInfo

st.set_page_config(
    page_title="SILVERMIC Evening ORB Paper Bot",
    page_icon="📈",
    layout="wide"
)

DB = "paper_state.db"
IST = ZoneInfo("Asia/Kolkata")
CAPITAL = 30000
RISK_LIMIT = 300
MAX_TRADES = 1

def connect_db():
    return sqlite3.connect(DB)

def init_db():
    with connect_db() as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                day TEXT,
                side TEXT,
                entry REAL,
                sl REAL,
                target REAL,
                risk_points REAL,
                qty INTEGER,
                high_water REAL,
                low_water REAL,
                extensions INTEGER DEFAULT 0,
                status TEXT,
                exit_price REAL,
                pnl REAL DEFAULT 0
            )
        """)

def get_open_trade(day):
    with connect_db() as con:
        con.row_factory = sqlite3.Row
        row = con.execute(
            "SELECT * FROM trades WHERE day=? AND status='OPEN' "
            "ORDER BY id DESC LIMIT 1", (day,)
        ).fetchone()
        return dict(row) if row else None

def get_trades(day):
    with connect_db() as con:
        con.row_factory = sqlite3.Row
        rows = con.execute(
            "SELECT * FROM trades WHERE day=? ORDER BY id DESC", (day,)
        ).fetchall()
        return [dict(r) for r in rows]

def create_trade(day, side, entry, sl_distance, qty):
    risk_points = sl_distance
    sl = entry - risk_points if side == "BUY" else entry + risk_points
    target = entry + 2*risk_points if side == "BUY" else entry - 2*risk_points

    with connect_db() as con:
        con.execute("""
            INSERT INTO trades
            (day, side, entry, sl, target, risk_points, qty,
             high_water, low_water, extensions, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 'OPEN')
        """, (day, side, entry, sl, target, risk_points,
              qty, entry, entry))

def update_trade(trade, price):
    side = trade["side"]
    entry = trade["entry"]
    risk = trade["risk_points"]
    sl = trade["sl"]
    target = trade["target"]
    high = max(trade["high_water"], price)
    low = min(trade["low_water"], price)
    extensions = trade["extensions"]
    status = "OPEN"
    exit_price = None

    if side == "BUY":
        if high >= entry + risk:
            sl = max(sl, entry, high - risk)
        if price <= sl:
            status, exit_price = "CLOSED — SL", price
        elif price >= target:
            if extensions < 2:
                target += risk
                extensions += 1
            else:
                status, exit_price = "CLOSED — TARGET", price
    else:
        if low <= entry - risk:
            sl = min(sl, entry, low + risk)
        if price >= sl:
            status, exit_price = "CLOSED — SL", price
        elif price <= target:
            if extensions < 2:
                target -= risk
                extensions += 1
            else:
                status, exit_price = "CLOSED — TARGET", price

    pnl = 0
    if exit_price is not None:
        pnl = ((exit_price - entry) if side == "BUY"
               else (entry - exit_price)) * trade["qty"]

    with connect_db() as con:
        con.execute("""
            UPDATE trades
            SET sl=?, target=?, high_water=?, low_water=?,
                extensions=?, status=?, exit_price=?, pnl=?
            WHERE id=?
        """, (sl, target, high, low, extensions,
              status, exit_price, pnl, trade["id"]))

init_db()

now = datetime.now(IST)
day = now.strftime("%Y-%m-%d")
clock = now.time()

st.title("SILVERMIC Evening ORB — Paper Bot")
st.warning(
    "PAPER MODE ONLY. Dhan live data இணைக்கப்படவில்லை. "
    "இந்த app உண்மையான orders அனுப்பாது."
)

c1, c2, c3 = st.columns(3)
c1.metric("Capital", f"₹{CAPITAL:,}")
c2.metric("Risk limit / trade", f"₹{RISK_LIMIT}")
c3.metric("ORB", "17:00–18:00 IST")

st.caption("Entry signals: 18:00 IST-க்கு பிறகு மட்டும்.")
st.subheader("1. ORB Range — manual entry")

with st.form("orb_form"):
    orb_high = st.number_input("5–6 PM ORB High", min_value=0.0, value=0.0)
    orb_low = st.number_input("5–6 PM ORB Low", min_value=0.0, value=0.0)
    save_orb = st.form_submit_button("Check ORB range")

if save_orb:
    if orb_high <= orb_low or orb_low <= 0:
        st.error("High மற்றும் Low சரியாக உள்ளிடுங்கள்.")
    elif clock < time(18, 0):
        st.warning("Entry நேரம் 6:00 PM-க்கு பிறகு மட்டுமே.")
    else:
        st.session_state["orb_high"] = orb_high
        st.session_state["orb_low"] = orb_low
        st.success("ORB range ஏற்றுக்கொள்ளப்பட்டது.")

st.subheader("2. Paper Entry")

with st.form("entry_form"):
    side = st.selectbox("Direction", ["BUY", "SELL"])
    entry = st.number_input("Entry price (manual)", min_value=0.0, value=0.0)
    sl_distance = st.number_input("SL distance in price points", min_value=0.01, value=5.0)
    qty = st.number_input("Contract quantity", min_value=1, value=1, step=1)
    open_btn = st.form_submit_button("Create paper trade")

trades = get_trades(day)
open_trade = get_open_trade(day)

if open_btn:
    high = st.session_state.get("orb_high")
    low = st.session_state.get("orb_low")

    if clock < time(18, 0):
        st.error("6:00 PM-க்கு முன் entry அனுமதி இல்லை.")
    elif high is None or low is None:
        st.error("முதலில் ORB High/Low உள்ளிடுங்கள்.")
    elif entry <= 0:
        st.error("Entry price சரியாக உள்ளிடுங்கள்.")
    elif side == "BUY" and entry <= high:
        st.error("BUY entry-க்கு price ORB High-க்கு மேல் இருக்க வேண்டும்.")
    elif side == "SELL" and entry >= low:
        st.error("SELL entry-க்கு price ORB Low-க்கு கீழே இருக்க வேண்டும்.")
    elif open_trade:
        st.error("ஏற்கெனவே ஒரு paper trade OPEN-ல் உள்ளது.")
    elif len(trades) >= MAX_TRADES:
        st.error("இன்றைய paper trade limit முடிந்தது.")
    elif qty * sl_distance > RISK_LIMIT:
        st.error("Quantity × SL distance ₹300-ஐ மீறுகிறது.")
    else:
        create_trade(day, side, entry, sl_distance, int(qty))
        st.success("Paper trade உருவாக்கப்பட்டது. Live order அனுப்பப்படவில்லை.")
        st.rerun()

st.subheader("3. Trailing SL + Target")

open_trade = get_open_trade(day)

if open_trade:
    st.write(f"Direction: **{open_trade['side']}**")
    st.write(f"Entry: ₹{open_trade['entry']:.2f}")
    st.write(f"Current SL: ₹{open_trade['sl']:.2f}")
    st.write(f"Current Target: ₹{open_trade['target']:.2f}")
    st.write(f"Target extensions: {open_trade['extensions']}/2")

    with st.form("price_update"):
        current_price = st.number_input(
            "Current price (manual)",
            min_value=0.0, value=float(open_trade["entry"])
        )
        update_btn = st.form_submit_button("Update paper price")

    if update_btn:
        if current_price <= 0:
            st.error("சரியான price உள்ளிடுங்கள்.")
        else:
            update_trade(open_trade, current_price)
            st.rerun()
else:
    st.info("இப்போது OPEN paper trade இல்லை.")

st.subheader("4. Today's Paper Trade Log")
trades = get_trades(day)

if trades:
    st.dataframe(trades, use_container_width=True)
    closed_pnl = sum(t["pnl"] for t in trades if t["status"].startswith("CLOSED"))
    st.metric("Closed paper P&L (before charges)", f"₹{closed_pnl:.2f}")
else:
    st.info("இன்று paper trades பதிவு செய்யப்படவில்லை.")

st.caption(
    "குறிப்பு: SQLite state app restart-க்கு சில சூழல்களில் நீடிக்கலாம்; "
    "Streamlit Cloud local storage நிரந்தரமாக இருக்கும் என உத்தரவாதம் இல்லை. "
    "நிரந்தர சேமிப்புக்கு வெளிப்புற database தேவை."
)
