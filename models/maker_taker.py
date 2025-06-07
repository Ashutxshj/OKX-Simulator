# P(maker) = 1 / (1 + exp(–(β₀ + β₁x₁ + ...)))
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
import pandas as pd

def calculate_maker_taker_proportion(orderbook_list):
    if len(orderbook_list) < 2:
        return pd.DataFrame(columns=["timestamp", "mid_price", "prob_maker", "prob_taker"])

    try:
        df = pd.DataFrame(orderbook_list)
        df = df.astype({
            "top_bid_price": float,
            "top_bid_qty": float,
            "top_ask_price": float,
            "top_ask_qty": float
        })

        df["spread"] = df["top_ask_price"] - df["top_bid_price"]
        df["mid_price"] = (df["top_ask_price"] + df["top_bid_price"]) / 2
        df["next_mid"] = df["mid_price"].shift(-1)
        df.dropna(inplace=True)
        df["taker_label"] = (df["next_mid"] > df["mid_price"]).astype(int)

        X = df[["spread", "top_bid_qty", "top_ask_qty"]]
        y = df["taker_label"]

        if len(set(y)) < 2:
            df["prob_maker"] = 1.0
            df["prob_taker"] = 0.0
            return df[["timestamp", "mid_price", "prob_maker", "prob_taker"]]

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        model = LogisticRegression()
        model.fit(X_scaled, y)

        probs = model.predict_proba(X_scaled)
        df["prob_maker"] = probs[:, 0]
        df["prob_taker"] = probs[:, 1]

        return df[["timestamp", "mid_price", "prob_maker", "prob_taker"]]

    except Exception as e:
        print(f"⚠️ Error in maker-taker model: {e}")
        return pd.DataFrame(columns=["timestamp", "mid_price", "prob_maker", "prob_taker"])
