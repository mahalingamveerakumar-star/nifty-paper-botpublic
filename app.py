import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo

st.set_page_config(page_title="NIFTY + SILVERMIC Paper Dashboard", page_icon="📊", layout="wide")
IST = ZoneInfo("Asia/Kolkata")
CAPITAL = 30000.0
RISK_PER_TRADE = 300.0

st.title("📊 NIFTY + SILVERMIC — Manual Paper Trading")
st.warning("PAPER MODE ONLY • Dhan API/live data இல்லை • எந்த real order-மும் அனுப்பப்படாது.")
st.caption(f"இந்திய நேரம்: {datetime.now(IST).strftime('%d-%m-%Y %I:%M:%S %p')} IST")

a, b, c = st.columns(3)
a.metric("Paper Capital", f"₹{CAPITAL:,.0f}")
b.metric("Risk / Trade", f"₹{RISK_PER_TRADE:,.0f}")
c.metric("Mode", "Manual Paper Only")

if "paper_trades" not in st.session_state:
    st.session_state.paper_trades = []

tabs = st.tabs(["🌅 NIFTY", "🌆 SILVERMIC", "📒 Trade Log", "ℹ️ Rules"])

def add_trade(symbol, entry, sl, target, qty, direction, note):
    if min(entry, sl, target, qty) <= 0:
        st.error("Entry, SL, Target, Quantity அனைத்தும் 0-ஐ விட அதிகமாக இருக்க வேண்டும்.")
        return
    if direction == "BUY" and not (sl < entry < target):
        st.error("BUY-க்கு SL < Entry < Target இருக்க வேண்டும்.")
        return
    if direction == "SELL" and not (target < entry < sl):
        st.error("SELL-க்கு Target < Entry < SL இருக்க வேண்டும்.")
        return
    risk = abs(entry - sl) * qty
    reward = abs(target - entry) * qty
    if risk > RISK_PER_TRADE:
        st.error(f"கணக்கிடப்பட்ட risk ₹{risk:,.2f}; ₹{RISK_PER_TRADE:,.0f} வரம்பை மீறுகிறது. Quantity குறைக்கவும்.")
        return
    st.session_state.paper_trades.append({
        "time": datetime.now(IST).strftime("%d-%m-%Y %H:%M:%S"),
        "symbol": symbol, "direction": direction, "entry": float(entry),
        "sl": float(sl), "target": float(target), "qty": int(qty),
        "risk": float(risk), "reward": float(reward), "status": "OPEN",
        "exit": None, "pnl": 0.0, "note": note
    })
    st.success(f"{symbol} paper trade பதிவு செய்யப்பட்டது. Risk ₹{risk:,.2f}; planned reward ₹{reward:,.2f}.")

with tabs[0]:
    st.header("NIFTY — Morning ORB")
    st.write("**Opening Range:** 9:15–9:30 AM IST • 5-minute chart")
    st.info("NIFTY index level அல்லது option premium பயன்படுத்தலாம். Entry, SL, Target அனைத்தும் ஒரே instrument/price basis-ல் இருக்க வேண்டும்.")
    with st.form("nifty_form"):
        x, y = st.columns(2)
        with x:
            direction = st.radio("Direction", ["BUY", "SELL"], horizontal=True, key="n_dir")
            entry = st.number_input("Entry price", min_value=0.0, value=0.0, step=0.05, key="n_entry")
            sl = st.number_input("Stop Loss", min_value=0.0, value=0.0, step=0.05, key="n_sl")
        with y:
            target = st.number_input("Target (1:2)", min_value=0.0, value=0.0, step=0.05, key="n_target")
            qty = st.number_input("Quantity / units", min_value=1, value=1, step=1, key="n_qty")
            note = st.text_input("Notes", placeholder="ORB close + VWAP + volume manually checked", key="n_note")
        if st.form_submit_button("Add NIFTY Paper Trade", type="primary"):
            add_trade("NIFTY", entry, sl, target, qty, direction, note)

with tabs[1]:
    st.header("SILVERMIC — Evening ORB")
    st.write("**Opening Range:** 5:00–6:00 PM IST • 5-minute chart")
    st.info("MCX chart-ல் ORB High/Low மற்றும் breakout candle close-ஐ manual-ஆகச் சரிபார்த்து values உள்ளிடவும். Contract lot/tick value-ஐ உங்கள் தற்போதைய contract specification-ல் உறுதிசெய்யவும்.")
    with st.form("silver_form"):
        x, y = st.columns(2)
        with x:
            direction = st.radio("Direction", ["BUY", "SELL"], horizontal=True, key="s_dir")
            entry = st.number_input("Entry price", min_value=0.0, value=0.0, step=0.05, key="s_entry")
            sl = st.number_input("Stop Loss", min_value=0.0, value=0.0, step=0.05, key="s_sl")
        with y:
            target = st.number_input("Target (1:2)", min_value=0.0, value=0.0, step=0.05, key="s_target")
            qty = st.number_input("Quantity / units", min_value=1, value=1, step=1, key="s_qty")
            note = st.text_input("Notes", placeholder="ORB close + VWAP + volume manually checked", key="s_note")
        if st.form_submit_button("Add SILVERMIC Paper Trade", type="primary"):
            add_trade("SILVERMIC", entry, sl, target, qty, direction, note)

with tabs[2]:
    st.header("Trade Log")
    trades = st.session_state.paper_trades
    if not trades:
        st.write("இன்னும் paper trades பதிவு செய்யப்படவில்லை.")
    for i, trade in enumerate(trades):
        with st.expander(f"{i+1}. {trade['symbol']} {trade['direction']} — {trade['status']} — {trade['time']}"):
            x, y, z = st.columns(3)
            x.metric("Entry", f"{trade['entry']:,.2f}")
            y.metric("Stop Loss", f"{trade['sl']:,.2f}")
            z.metric("Target", f"{trade['target']:,.2f}")
            st.write(f"Quantity: {trade['qty']} | Planned risk: ₹{trade['risk']:,.2f} | Planned reward: ₹{trade['reward']:,.2f}")
            if trade["status"] == "OPEN":
                with st.form(f"close_{i}"):
                    exit_price = st.number_input("Manual exit price", min_value=0.0, value=0.0, step=0.05, key=f"exit_{i}")
                    if st.form_submit_button("Close paper trade"):
                        if exit_price <= 0:
                            st.error("சரியான exit price உள்ளிடுங்கள்.")
                        else:
                            pnl = (exit_price - trade["entry"]) * trade["qty"]
                            if trade["direction"] == "SELL":
                                pnl = -pnl
                            trade["exit"] = float(exit_price)
                            trade["pnl"] = float(pnl)
                            trade["status"] = "CLOSED"
                            st.rerun()
            else:
                st.write(f"Exit: {trade['exit']:,.2f} | Realized paper P&L: ₹{trade['pnl']:,.2f}")
    closed = [t for t in trades if t["status"] == "CLOSED"]
    total_pnl = sum(t["pnl"] for t in closed)
    x, y, z = st.columns(3)
    x.metric("Closed trades", len(closed))
    y.metric("Open trades", sum(t["status"] == "OPEN" for t in trades))
    z.metric("Realized Paper P&L", f"₹{total_pnl:,.2f}")
    if st.button("Clear all paper trades"):
        st.session_state.paper_trades = []
        st.rerun()

with tabs[3]:
    st.header("Rules & Limitations")
    st.markdown("""
- NIFTY ORB: 9:15–9:30 AM IST. SILVERMIC ORB: 5:00–6:00 PM IST.
- Entry முன் 5-minute candle close, VWAP, volume ஆகியவற்றை chart-ல் manual-ஆகச் சரிபார்க்கவும்.
- BUY: SL < Entry < Target. SELL: Target < Entry < SL.
- 1:2 example: Entry 100, SL 98 என்ற BUY trade-க்கு Target 104.
- App risk = abs(Entry − SL) × quantity எனக் கணக்கிடுகிறது. Futures/options contract multiplier அல்லது lot value வேறுபட்டால் உண்மையான risk வேறாக இருக்கலாம்; சரியான contract specification-ஐ உறுதிசெய்யவும்.
- Live prices, VWAP, volume, ORB levels fetch ஆகாது; automatic signals/alerts/trailing SL இல்லை.
