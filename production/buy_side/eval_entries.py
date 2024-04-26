
from scipy.stats import norm
import numpy as np
import requests
import datetime as dt
def get_markets_tb(month, dayofmonth):
    kalshi_url = f"https://trading-api.kalshi.com/trade-api/v2/events/INX-24{month}{dayofmonth}"
    kalshi_response = requests.get(kalshi_url).json()
    lst = []
    for i in kalshi_response["markets"]:
        if 3<i["yes_ask"]<97:
            lst.append(i["ticker"])

    less_markets = []
    between_markets = []
    greater_markets = []
    for i in range(len(lst)):
        market_url = f"https://trading-api.kalshi.com/trade-api/v2/markets/{lst[i]}"
        market = requests.get(market_url).json()["market"]
        if market["strike_type"]== "between":
            between_markets.append([market["ticker"], market["floor_strike"], market["cap_strike"], market["yes_ask"], market["no_ask"], market["yes_bid"]])
        if market["strike_type"] == "greater":
            greater_markets.append([market["ticker"], market["floor_strike"], market["yes_ask"], market["no_ask"], market["yes_bid"]])
        if market["strike_type"] == "less":
            less_markets.append([market["ticker"], market["cap_strike"], market["yes_ask"], market["no_ask"], market["yes_bid"]])
    
    return less_markets, greater_markets, between_markets



def get_prospects(curr_price, curr_std, dayofmonth, month):
    less_markets, greater_markets, between_markets = get_markets_tb(month, dayofmonth)
    lambda_dict = {}
    to_write = []
    for i in less_markets:
        our_z = (i[1]-curr_price)/curr_std
        our_p = norm.cdf(our_z)
        
        if 100*(our_p) > i[2] + 1:
            lambda_dict[f"{i[0]}"] = ["yes", (100*our_p)-i[2], i[2], 100*our_p, "less"]

        if 100*(1-our_p) > i[3] + 1:
            lambda_dict[f"{i[0]}"] = ["no",(100*(1-our_p))-i[3], i[3], 100*(1-our_p), "less"]
        to_write.append([dt.datetime.now().isoformat(),i[0],100*our_p-i[2], i[4],i[2]])
        
        
    for i in between_markets:
        z1 = (i[1]-curr_price)/curr_std
        z2 = (i[2]-curr_price)/curr_std
        
        p_between = norm.cdf(z2) - norm.cdf(z1)
        print(p_between)
        if 100*(p_between) > i[3] + 1:
            lambda_dict[f"{i[0]}"] = ["yes",(100*p_between)-i[3], i[3], 100*p_between, "between"]
        if 100*(1-p_between) > i[4] + 1:
            lambda_dict[f"{i[0]}"] = ["no", (100*(1-p_between))-i[4], i[4], 100*(1-p_between), "between"]
        to_write.append([dt.datetime.now().isoformat(), i[0], (100*p_between)-i[3], i[5], i[3]])

    for i in greater_markets:
        our_z = (curr_price-i[1])/curr_std
        p_great = norm.cdf(our_z)
        if 100*(p_great) > i[2] + 1:
            lambda_dict[f"{i[0]}"] = ["yes", (100*p_great)-i[2], i[2], 100*p_great, "greater"]
        if 100*(1-p_great) > i[3] + 1:
            lambda_dict[f"{i[0]}"] = ["no", (100*(1-p_great))-i[3], i[3], 100*(1-p_great), "greater"]
        to_write.append([dt.datetime.now().isoformat(),i[0],(100*our_p)-i[2], i[4], i[2]])
    print(lambda_dict)
    return lambda_dict, to_write