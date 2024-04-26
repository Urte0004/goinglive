from production.sell_side.fetch_markets_ts import get_markets_ts
from scipy.stats import norm

def get_sells(positions, curr_price, curr_std):
    tsl_markets, tsg_markets, tsb_markets = get_markets_ts(positions)
    sells = []
    evals = {}

    for i in tsl_markets:
        our_z = (i[1]-curr_price)/curr_std
        our_p = norm.cdf(our_z)
        if (i[4] == "no"):
            evals[f"{i[0]}"] = i[3]
            if ((1-our_p)*100<=i[3]):
                sells.append(i[0])
        if (i[4] == "yes"):
            evals[f"{i[0]}"] = i[2]
            if ((our_p*100) <= i[2]):
                sells.append(i[0])
    for i in tsg_markets:
        our_z = (i[1] - curr_price)/curr_std
        our_p = norm.cdf(our_z)
        if (i[4] == "no"):
            evals[f"{i[0]}"] = i[3]
            if (100*(1-our_p)) <= i[3]:
                sells.append(i[0])
        if (i[4] == "yes"):
            evals[f"{i[0]}"] = i[2]
            if ((our_p*100) <= i[2]):
                sells.append(i[0])
    for i in tsb_markets:
        z1 = (i[1] - curr_price)/curr_std
        z2 = (i[2] - curr_price)/curr_std
        our_p = norm.cdf(z2) - norm.cdf(z1)
        if (i[5] == "no"):
            evals[f"{i[0]}"] = i[4]
            if (100*(1-our_p)) <= i[4]:
                sells.append(i[0])
        if (i[5] == "yes"):
            evals[f"{i[0]}"] = i[3]
            if (100*our_p <= i[3]):
                sells.append(i[0])
    return evals, sells
    
        
        
    

        
        

        
        
        
    