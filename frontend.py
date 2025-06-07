import streamlit as st
import time
import pandas as pd
import redis
import pickle

from models.slippage import get_all_slippage_predictions
from models.maker_taker import calculate_maker_taker_proportion
from models.market_impact import calculate_expected_market_impact
from models.fees import calculate_expected_fees

# Redis Client
r = redis.Redis(host="localhost", port=6379, db=0)

st.set_page_config(page_title="📈 OKX Orderbook Viewer", layout="wide")
st.title("📈 Real-Time OKX Orderbook Viewer")


st.sidebar.header("⚙️ Simulation Settings")
exchange = st.sidebar.selectbox("Exchange", ["OKX"])
asset = st.sidebar.selectbox("Asset", ["BTC/USDT", "ETH/USDT", "SOL/USDT"])
order_type = st.sidebar.selectbox("Order Type", ["Market"])
quantity_usd = st.sidebar.number_input("Order Quantity (USD)", min_value=10.0, value=100.0, step=10.0)
volatility = st.sidebar.slider("Volatility Estimate (%)", min_value=0.0, max_value=10.0, value=2.5)
fee_tier = st.sidebar.selectbox("Fee Tier", ["Maker", "Taker"])

placeholder = st.empty()

while True:
    try:
        raw_data = r.lrange("orderbook_rows", 0, -1)
        orderbook_rows = [pickle.loads(row) for row in raw_data]

        if len(orderbook_rows) < 2:
            placeholder.warning("⏳ Waiting for more live data...")
            time.sleep(1)
            continue

        df = pd.DataFrame(orderbook_rows)
        latest_data = df.iloc[-1].copy()
        bid_price = float(latest_data["top_bid_price"])
        ask_price = float(latest_data["top_ask_price"])

        slippage = get_all_slippage_predictions(orderbook_rows)[-1]
        fees = calculate_expected_fees(orderbook_rows, quantity_usd, fee_tier)
        market_impact = calculate_expected_market_impact(orderbook_rows, order_usd=quantity_usd, volatility=volatility / 100.0)
        maker_taker_df = calculate_maker_taker_proportion(orderbook_rows)
        latest_probs = maker_taker_df.iloc[-1]

        avg_latency = df["internal_latency_ms"].mean() if "internal_latency_ms" in df.columns else None
        net_cost = slippage + fees + market_impact

        maker_prob=latest_probs["prob_maker"]
        taker_prob=latest_probs["prob_taker"]
        maker_taker_ratio=maker_prob/taker_prob if taker_prob!=0 else float('inf')

        
        with placeholder.container():
            st.subheader(f"📊 Market Metrics for {asset} ({exchange})")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("💸 Expected Slippage", f"{slippage:.4f}")
                st.metric("📡 Avg Latency", f"{avg_latency:.2f} ms")
            with col3:
                st.metric("⚖️ Net Cost", f"${net_cost:.6f}")
                st.metric("🧠 Maker Prob", f"{latest_probs['prob_maker']:.6f}")
                st.metric("⚔️ Taker Prob", f"{latest_probs['prob_taker']:.6f}")
                st.metric(" Maker/Taker Ratio",f"{maker_taker_ratio:.3f}")
            with col2:
                st.metric("💰 Expected Fees", f"${fees:.3f}")
                st.metric("📉 Market Impact", f"{market_impact:.6f}")
            

    except Exception as e:
        placeholder.error(f"⚠️ Live data error: {e}")

    time.sleep(1)
