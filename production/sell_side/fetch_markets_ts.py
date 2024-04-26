import requests

def get_markets_ts(curr_positions):
    tsl_markets = []
    tsg_markets = []
    tsb_markets = []            
    for position in curr_positions.keys():
        market_url = f"https://trading-api.kalshi.com/trade-api/v2/markets/{position}"
        market = requests.get(market_url).json()
        market = market["market"]
        if market["strike_type"]== "between":
            tsb_markets.append([market["ticker"], market["floor_strike"], market["cap_strike"], market["yes_bid"], market["no_bid"], curr_positions[position][0]])
        if market["strike_type"] == "greater":
            tsg_markets.append([market["ticker"], market["floor_strike"], market["yes_bid"], market["no_bid"], curr_positions[position][0]])
        if market["strike_type"] == "less":
            tsl_markets.append([market["ticker"], market["cap_strike"], market["yes_bid"], market["no_bid"], curr_positions[position][0]])
    return tsl_markets, tsg_markets, tsb_markets
    