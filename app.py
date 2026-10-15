
import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="Dhan NIFTY Paper Bot",
    page_icon="📈",
    layout="wide"
)

st.title("NIFTY Options Paper Trading Bot")
st.caption("5-Minute ORB + VWAP | PAPER MODE ONLY")

st.warning("Paper Trading மட்டுமே. உண்மையான Dhan orders அனுப்பப்படாது.")

capital = 30000
risk = 300
max_trades = 3

col1, col2, col3 = st.columns(3)
col1.metric("Capital", "₹30,000")
col2.metric("Risk / Trade", "₹300")
col3.metric("Daily Trade Limit", "3")

st.subheader("Strategy")
st.write("Opening Range: 9:15 AM – 9:20 AM")
st.write("Entry: Opening Range breakout + VWAP + Volume confirmation")
st.write("Target: 1:2 Risk–Reward")

if "trades" not in st.session_state:
    st.session_state.trades = []

st.subheader("Paper Trade Simulator")

with st.form("trade_form"):
    side = st.selectbox("Option", ["CE", "PE"])
    entry = st.number_input("Entry Premium (₹)", min_value=0.05, value=100.0)
    sl_points = st.number_input("SL per unit (₹)", min_value=0.05, value=5.0)
    qty = st.number_input("Quantity (units)", min_value=1, value=50, step=1)

    submit = st.form_submit_button("Simulate Paper BUY")

if submit:
    if len(st.session_state.trades) >= max_trades:
        st.error("Daily maximum 3 trades reached.")
    elif qty * sl_points > risk:
        st.error("Risk ₹300-ஐ மீறுகிறது. Quantity அல்லது SL-ஐ குறைக்கவும்.")
    else:
        st.session_state.trades.append({
            "Time": datetime.now().strftime("%H:%M:%S"),
            "Option": side,
            "Entry": entry,
            "SL": round(entry - sl_points, 2),
            "Target": round(entry + 2 * sl_points, 2),
            "Quantity": int(qty),
            "Planned Risk": round(qty * sl_points, 2),
            "Status": "PAPER — NOT EXECUTED"
        })
        st.success("Paper trade பதிவு செய்யப்பட்டது.")

st.subheader("Trade Log")

if st.session_state.trades:
    st.dataframe(pd.DataFrame(st.session_state.trades), use_container_width=True)
else:
    st.info("இன்னும் paper trades இல்லை.")
