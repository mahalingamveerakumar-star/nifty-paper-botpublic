
import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo

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

st.title("📊 NIFTY + SILVERMIC Paper Trading")
st.warning(
    "PAPER TRADING ONLY — Live market data இணைக்கப்படவில்லை. "
    "உண்மையான orders அனுப்பப்படாது."
)

c1, c2, c3 = st.columns(3)
c1.metric("Paper Capital", f"₹{CAPITAL:,.0f}")
c2.metric("Risk Limit / Trade", f"₹{RISK_LIMIT:,.0f}")
c3.metric("Mode", "Manual Paper Only")

tab_nifty, tab_silver, tab_log, tab_rules = st.tabs(
    ["📈 NIFTY", "🥈 SILVERMIC", "📒 Trade Log", "📘 Rules"]
)


def trade_form(symbol, tab):
    with tab:
        st.subheader(f"{symbol} — Manual Paper Trade")

        side = st.selectbox(
            "Trade Direction",
            ["BUY", "SELL"],
            key=f"{symbol}_side"
        )

        entry = st.number_input(
            "Entry Price",
            min_value=0.0,
            value=100.0,
            step=0.05,
            key=f"{symbol}_entry"
        )

        sl = st.number_input(
            "Stop Loss Price",
            min_value=0.0,
            value=98.0 if side == "BUY" else 102.0,
            step=0.05,
            key=f"{symbol}_sl"
        )

        qty = st.number_input(
            "Quantity",
            min_value=1,
            value=1,
            step=1,
            key=f"{symbol}_qty"
        )

        valid = (
            entry > 0
            and sl > 0
            and ((side == "BUY" and sl < entry)
                 or (side == "SELL" and sl > entry))
        )

        if valid:
            risk_per_unit = abs(entry - sl)
            risk_amount = risk_per_unit * qty

            if side == "BUY":
                target = entry + (risk_per_unit * 2)
            else:
                target = entry - (risk_per_unit * 2)

            a, b, c = st.columns(3)
            a.metric("Risk Amount", f"₹{risk_amount:,.2f}")
            b.metric("Target (1:2)", f"{target:,.2f}")
            c.metric("Potential Reward", f"₹{risk_amount * 2:,.2f}")

            if risk_amount > RISK_LIMIT:
                st.error(
                    "இந்த trade-ன் கணக்கிடப்பட்ட risk ₹300-ஐ மீறுகிறது. "
                    "Quantity அல்லது SL distance-ஐ குறைக்கவும்."
                )

            if st.button("Save Paper Trade", key=f"{symbol}_save"):
                if risk_amount > RISK_LIMIT:
                    st.error("Risk limit மீறுவதால் trade பதிவு செய்யப்படவில்லை.")
                else:
                    st.session_state.paper_trades.append({
                        "Time": datetime.now(IST).strftime("%d-%m-%Y %H:%M:%S"),
                        "Symbol": symbol,
                        "Side": side,
                        "Entry": entry,
                        "SL": sl,
                        "Target": round(target, 2),
                        "Quantity": qty,
                        "Risk": round(risk_amount, 2),
                        "Status": "OPEN"
                    })
                    st.success("Paper trade பதிவு செய்யப்பட்டது.")
                    st.rerun()
        else:
            st.error(
                "BUY-க்கு SL, Entry-ஐ விடக் குறைவாக இருக்க வேண்டும். "
                "SELL-க்கு SL, Entry-ஐ விட அதிகமாக இருக்க வேண்டும்."
            )


trade_form("NIFTY", tab_nifty)
trade_form("SILVERMIC", tab_silver)

with tab_log:
    st.subheader("Paper Trade History")

    trades = st.session_state.paper_trades

    if trades:
        st.dataframe(trades, use_container_width=True)
        total_risk = sum(float(t.get("Risk", 0)) for t in trades)_risk = sum(float(t.get("Risk", 0)) for t in trades)_risk = sum(float(t.get("Risk", 0)) for t in trades)_risk = sum(float(t.get("Risk", 0)) for t in trades)_risk = sum(float(t.get("Risk", 0)) for t in trades)_risk = sum(float(t.get("Risk", 0)) for t in trades)_risk = sum(t["Risk"] for t in trades)
        st.metric("Recorded Trade Risk total_risk = sum(float(t.get("Risk", 0)) for t in trades)_risk = sum(float(t.get("Risk", 0)) for t in trades)_risk = sum(float(t.get("Risk", 0)) for t in trades)_risk = sum(float(t.get("Risk", 0)) for t in trades)_risk = sum(float(t.get("Risk", 0)) for t in trades)_risk = sum(float(t.get("Risk", 0)) for t in trades)", f"₹{total_risk = sum(float(t.get("Risk", 0)) for t in trades)_risk = sum(float(t.get("Risk", 0)) for t in trades)_risk = sum(float(t.get("Risk", 0)) for t in trades)_risk = sum(float(t.get("Risk", 0)) for t in trades)_risk = sum(float(t.get("Risk", 0)) for t in trades)_risk = sum(float(t.get("Risk", 0)) for t in trades)_risk:,.2f}")

        if st.button("Clear All Paper Trades"):
            st.session_state.paper_trades = []
            st.rerun()
    else:
        st.info("இன்னும் paper trades பதிவு செய்யப்படவில்லை.")

with tab_rules:
    st.subheader("Rules & Limitations")
    st.markdown("""
    - Paper capital: ₹30,000.
    - Maximum planned risk per trade: ₹300.
    - Target calculation: 1:2 risk-reward.
    - BUY: Stop Loss < Entry < Target.
    - SELL: Target < Entry < Stop Loss.
    - இது manual paper simulator மட்டுமே.
    - Live prices, ORB, VWAP, volume signals இன்னும் இணைக்கப்படவில்லை.
    - Trade log, Streamlit session reset ஆனபோது மறையலாம்.
    - Brokerage, slippage, futures lot value ஆகியவை இதில் கணக்கிடப்படவில்லை.
    """)
