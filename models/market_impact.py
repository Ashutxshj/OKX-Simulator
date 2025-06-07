def calculate_expected_market_impact(
    orderbook_list,
    order_usd=100,
    volatility=0.02,     
    daily_volume_usd=1e7,  
    eta=0.1,
    lam=0.05
):
    try:
        if not orderbook_list or len(orderbook_list) == 0:
            return 0.0

        latest_snapshot = orderbook_list[-1]
        latest_price = float(latest_snapshot.get("top_ask_price", 0))

        if latest_price == 0:
            return 0.0

        Q = order_usd                    
        V = daily_volume_usd            
        σ = volatility                  

        # Almgren-Chriss Market Impact formula
        impact = eta * (Q / V) + 0.5 * lam * (σ ** 2) * (Q / V) ** 2
        return round(impact, 8)

    except Exception as e:
        print(f"⚠️ Error in market impact calculation: {e}")
        return 0.0
