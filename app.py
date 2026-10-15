
import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo

# -------------------- CONFIG --------------------

st.set_page_config(
    page_title="NIFTY + SILVERMIC Paper Dashboard",
    page_icon="📊",
    layout="wide"
)

CAPITAL = 30000.0
RISK_LIMIT = 300.0
IST = ZoneInfo("Asia/Kolkata")

if "paper_trades" not in st.session_state:
    st.session_state.paper_trades = []

# -------------------- HEADER --------------------

st.title("📊 NIFTY + SILVERMIC Paper Trading")

st.warning(
    "PAPER TRADING ONLY | Live market data இணைக்கப்படவில்லை. "
    "உண்மையான orders அனுப்பப்படாது."
)

col1, col2, col3 = st.columns(3)
col1.metric("Paper Capital", f"₹{CAPITAL:,.0f}")
col2.metric("Maximum Risk / Trade", f"₹{RISK_LIMIT:,.0f}")
col3.metric("Trading Mode", "Manual Paper Only")

st.caption(
    "இந்திய நேரம்: "
    + datetime.now(IST).strftime("%d-%m-%Y %I:%M:%S %p IST")
)

tab_nifty, tab_silver, tab_log, tab_rules = st.tabs(
    ["📈 NIFTY", "🥈 SILVERMIC", "📒 Trade Log", "📘 Rules"]
)

# -------------------- TRADE FORM --------------------

def show_trade_form(symbol, tab):
    with tab:
        st.subheader(f"{symbol} — Manual Paper Trade")

        side = st.radio(
            "Trade Direction",
            ["BUY", "SELL"],
            horizontal=True,
            key=f"{symbol}_side"
        )

        entry = st.number_input(
            "Entry Price",
            min_value=0.0,
            value=100.0,
            step=0.05,
            format="%.2f",
            key=f"{symbol}_entry"
        )

        default_sl = 98.0 if side == "BUY" else 102.0

        sl = st.number_input(
            "Stop Loss Price",
            min_value=0.0,
            value=default_sl,
            step=0.05,
            format="%.2f",
            key=f"{symbol}_sl_{side}"
        )

        qty = st.number_input(
            "Quantity",
            min_value=1,
            value=1,
            step=1,
            key=f"{symbol}_qty"
        )

        if side == "BUY":
            valid = entry > 0 and 0 < sl < entry
        else:
            valid = entry > 0 and sl > entry

        if not valid:
            st.error(
                "BUY: SL, Entry-ஐ விடக் குறைவாக இருக்க வேண்டும். "
                "SELL: SL, Entry-ஐ விட அதிகமாக இருக்க வேண்டும்."
            )
            return

        risk_per_unit = abs(entry - sl)
        risk_amount = risk_per_unit * qty

        if side == "BUY":
            target = entry + (risk_per_unit * 2)
        else:
            target = entry - (risk_per_unit * 2)

        a, b, c = st.columns(3)
        a.metric("Planned Risk", f"₹{risk_amount:,.2f}")
        b.metric("Target (1:2)", f"{target:,.2f}")
        c.metric("Potential Reward", f"₹{risk_amount * 2:,.2f}")

        if risk_amount > RISK_LIMIT:
            st.error(
                "Risk ₹300-ஐ மீறுகிறது. Quantity அல்லது SL distance-ஐ குறைக்கவும்."
            )

        if st.button("Save Paper Trade", key=f"{symbol}_save"):
            if risk_amount > RISK_LIMIT:
                st.error("Risk limit மீறுவதால் trade பதிவு செய்யப்படவில்லை.")
            else:
                trade = {
                    "Time": datetime.now(IST).strftime("%d-%m-%Y %H:%M:%S"),
                    "Symbol": symbol,
                    "Side": side,
                    "Entry": float(entry),
                    "SL": float(sl),
                    "Target": round(target, 2),
                    "Quantity": int(qty),
                    "Risk": round(risk_amount, 2),
                    "Status": "OPEN"
                }

                st.session_state.paper_trades.append(trade)
                st.success("Paper trade வெற்றிகரமாகப் பதிவு செய்யப்பட்டது.")
                st.rerun()


show_trade_form("NIFTY", tab_nifty)
show_trade_form("SILVERMIC", tab_silver)

# -------------------- TRADE LOG --------------------

with tab_log:
    st.subheader("📒 Paper Trade History")

    trades = st.session_state.paper_trades

    if trades:
        st.dataframe(trades, use_container_width=True)

        # Missing Risk fields in old session records will not crash the app.
        total_risk = sum(
            float(trade.get("Risk", 0) or 0)
            for trade in trades
        )

        st.metric("Total Recorded Risk", f"₹{total_risk:,.2f}")
        st.caption(f"Total recorded trades: {len(trades)}")

        if st.button("Clear All Paper Trades"):
            st.session_state.paper_trades = []
            st.rerun()
    else:
        st.info("இன்னும் paper trades பதிவு செய்யப்படவில்லை.")

# -------------------- RULES --------------------

with tab_rules:
    st.subheader("Rules & Limitations")

    st.markdown("""
    **Capital & Risk**
    - Paper capital: ₹30,000.
    - Maximum planned risk per trade: ₹300.
    - Target calculation: 1:2 risk-reward.

    **Trade Direction**
    - BUY: Stop Loss < Entry < Target.
    - SELL: Target < Entry < Stop Loss.

    **Current Limitations**
    - இது manual paper trading simulator மட்டுமே.
    - Live market prices இன்னும் இணைக்கப்படவில்லை.
    - Automatic ORB, VWAP, Volume signals இன்னும் இல்லை.
    - Real orders அனுப்பப்படாது.
    - Brokerage, slippage மற்றும் contract lot value கணக்கிடப்படவில்லை.
    - Trade log session reset அல்லது app restart-ல் மறையலாம்.
    """)
