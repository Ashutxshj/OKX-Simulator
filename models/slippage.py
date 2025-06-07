#! Slippage = C0 + C1 (Q/V) 
from sklearn.linear_model import LinearRegression
import numpy as np
import pandas as pd

def train_slippage_model(orderbook_rows):
    if not orderbook_rows or len(orderbook_rows) < 2:
        return None, None

    df = pd.DataFrame(orderbook_rows)
    df["top_bid_price"] = pd.to_numeric(df["top_bid_price"], errors="coerce")
    df["top_ask_price"] = pd.to_numeric(df["top_ask_price"], errors="coerce")
    df.dropna(subset=["top_bid_price", "top_ask_price"], inplace=True)

    df=df[df["top_bid_price"]<=df["top_ask_price"]]

    df["slippage"] = df["top_ask_price"] - df["top_bid_price"]

    if df.empty:
        return None, None
    X = df[["top_bid_price", "top_ask_price"]]
    y = df["slippage"]

    model = LinearRegression()
    model.fit(X, y)
    return model, df


def predict_slippage(bid_price, ask_price, orderbook_rows):
    model, _ = train_slippage_model(orderbook_rows)
    if model is None:
        return 0.0
    input_features = np.array([[bid_price, ask_price]])
    return model.predict(input_features)[0]


def get_all_slippage_predictions(orderbook_rows):
    model, df = train_slippage_model(orderbook_rows)
    if model is None:
        return []
    X = df[["top_bid_price", "top_ask_price"]]
    return model.predict(X)
