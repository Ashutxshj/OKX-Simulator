FEE_TIERS = {
    "Maker": 0.045,
    "Taker": 0.050,
}

def calculate_expected_fees(orderbook_rows, usd_quantity=100, fee_tier="Maker"):
    fee_rate = FEE_TIERS.get(fee_tier, 0.0005)

    fees = []
    for snapshot in orderbook_rows:
        ask_price = snapshot.get("top_ask_price")
        if not ask_price:
            fees.append(0.0)
            continue

        quantity = usd_quantity / ask_price
        fee = ask_price * quantity * fee_rate
        fees.append(fee)

    return fees[-1]
