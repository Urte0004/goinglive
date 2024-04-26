import numpy as np
def sizes(total_cash, total_capital, lambda_dict, curr_positions):
    #fraction of capital
    frac = .8
    curr_invested = total_capital-total_cash
    bettable_capital = frac*total_capital
    if curr_invested >= bettable_capital:
        return [[i, 0] for i in lambda_dict.keys()]
    
    curr_bettable = bettable_capital - curr_invested
    
    #sizes in cent terms
    #working, but must set pos limits on markets.


    sizes = [curr_bettable*((1-(poten[2]/100))*((poten[3]/100)-((1-(poten[3]/100))/((100-poten[2])/poten[2])))) for poten in lambda_dict.values()]
    market_info = []
    for i in range(len(sizes)):
        if sizes[i] <= 100:
            market_info.append([list(lambda_dict.keys())[i], 0])
        elif list(lambda_dict.keys())[i] in list(curr_positions.keys()):
            market_info.append([list(lambda_dict.keys())[i], 0])
            print('worked')
        else:
             market_info.append([list(lambda_dict.keys())[i], sizes[i]])

    return market_info