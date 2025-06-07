import asyncio
import websockets
import json
from datetime import datetime, timezone
import redis
import pickle
import redis.asyncio as aioredis

# Connect to Redis
r = aioredis.Redis(host='localhost', port=6379, db=0)

# Redis keys
ORDERBOOK_LATEST_KEY = "orderbook_data"
ORDERBOOK_HISTORY_KEY = "orderbook_rows"

async def get_orderbook_data():
    url = "wss://ws.gomarket-cpp.goquant.io/ws/l2-orderbook/okx/BTC-USDT-SWAP"
    
    print("🔌 Connecting to WebSocket...")
    async with websockets.connect(url, ping_interval=20, ping_timeout=10) as ws:
        print("✅ Connected. Receiving data...")

        while True:
            try:
                raw = await ws.recv()
                data = json.loads(raw)

                bids = data.get("bids", [])
                asks = data.get("asks", [])
                timestamp = data.get("timestamp")

                if not (bids and asks and timestamp):
                    continue

                ex_ts = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                local_ts = datetime.now(timezone.utc)
                internal_latency_ms = (local_ts - ex_ts).total_seconds() * 1000

                top_bid_price, top_bid_qty = bids[0]
                top_ask_price, top_ask_qty = asks[0]

                # Compose row
                row = {
                    "timestamp": timestamp,
                    "top_bid_price": float(top_bid_price),
                    "top_bid_qty": float(top_bid_qty),
                    "top_ask_price": float(top_ask_price),
                    "top_ask_qty": float(top_ask_qty),
                    "internal_latency_ms": internal_latency_ms
                }

                await r.set(ORDERBOOK_LATEST_KEY, pickle.dumps(row))

                await r.rpush(ORDERBOOK_HISTORY_KEY, pickle.dumps(row))

                print(f"📈 Tick @ {timestamp} | Bid: {top_bid_price} | Ask: {top_ask_price} | Latency: {internal_latency_ms:.2f} ms")
                await asyncio.sleep(0)

            except Exception as e:
                print(f"⚠️ Error: {e}")
                break

if __name__ == "__main__":
    asyncio.run(get_orderbook_data())
