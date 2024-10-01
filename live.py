import datetime as dt
import numpy as np
import pandas as pd
import time
import csv
import requests
import os


from production.orchestration.position_sizing import sizes
from production.orchestration.authenticate import login, key_12
from production.orchestration.fetch_m_twelve import fetch

from production.buy_side.eval_entries import get_prospects

from production.sell_side.eval_positions import get_sells
from production.orchestration.parse_perf import get_cash_and_capital
from production.orchestration.get_month_str import month_int_to_string

os.environ["TZ"] = "America/New_York"
time.tzset()
login()

#big old closed loop

stock_ticker = "GSPC"

curr_positions = {}

trades = open("production/portfolio/trades.csv", "a")
trader = csv.writer(trades)

kalshi_data = open("kalshi_collected/apr1124.csv", "a")
kalshi_collector = csv.writer(kalshi_data)

portfolio = open("production/portfolio/performance.csv", "r")

perform = open("production/portfolio/performance.csv", "a")
performer = csv.writer(perform)
key = key_12

#must start before open
while True:
    if 1<=dt.datetime.now().isoweekday() <=5:
        today = dt.datetime.now().date()
        #changing for when starting midday
        if (dt.datetime.now().hour * 60) + dt.datetime.now().minute < 924:
        
            if dt.datetime.now().isoweekday() == 1:

                day = (dt.datetime.now() - dt.timedelta(days=3)).date()
            else:
                day = (dt.datetime.now() - dt.timedelta(days=1)).date()
            yesterday_twelve = requests.get(f"https://api.twelvedata.com/time_series?apikey={key}&interval=1min&symbol={stock_ticker}&start_date={day} 09:30:00&end_date={day} 16:00:00").json()
            df = pd.DataFrame(yesterday_twelve['values'])
            df["close"] = [float(i) for i in df["close"]]
            
            df["diff"] = df["close"].diff()
            
            std = df["diff"].std()
            print(std)
            dayofmonth = dt.datetime.today().day
            month = month_int_to_string[dt.datetime.today().month]
            secs_till_open = (dt.datetime.combine(date=today ,time=dt.time(hour=10, minute=0)) - dt.datetime.now()).total_seconds()
            print("sleeping till open")
            #time.sleep(secs_till_open)
        while dt.time(hour=10,minute=0) < dt.datetime.now().time() < dt.time(hour=16,minute=0):
            curr_price, curr_std = fetch(key, stock_ticker, today, std)
            
            lambda_dict, to_write = get_prospects(curr_price, curr_std, dayofmonth, month)
            
            for row in to_write:
                print(row)
                kalshi_collector.writerow(row)
            kalshi_data.flush()
            #evaluate exits before entries
            
            cash, capital = get_cash_and_capital(portfolio)
            if dt.datetime.now().hour*60 + dt.datetime.now().minute <930:
                size_list = sizes(cash, capital, lambda_dict, curr_positions)
                for market in size_list:
                    
                    requery_url = f"https://trading-api.kalshi.com/trade-api/v2/markets/{market[0]}"
                    resp_for_testing = requests.get(requery_url).json()["market"]
                    prev_ask = lambda_dict[f"{market[0]}"][2]
                    if prev_ask <= market[1]:
                        side = lambda_dict[f"{market[0]}"][0]
                        curr_bid = resp_for_testing[f"{side}_bid"]
                        curr_ask = resp_for_testing[f"{side}_ask"]
                        #test for same ask before entering (or do fill or kill)
                        
                        if curr_ask == prev_ask:
                            n_contracts = market[1] // curr_ask
                            trader.writerow([
                                dt.datetime.now().isoformat(),
                                market[0],
                                n_contracts,
                                side,
                                curr_ask,
                                lambda_dict[f"{market[0]}"][1]]
                            )
                            trades.flush()

                            if market[0] in curr_positions.keys():
                                curr_positions[f"{market[0]}"][2] += n_contracts
                                curr_positions[f"{market[0]}"][1] = curr_bid
                                cash -= n_contracts*curr_ask
                                
                                
                            else:
                                curr_positions[f"{market[0]}"] = [side, curr_bid, n_contracts]
                                cash -= n_contracts *curr_ask

            #start exit processes
            pos_changes, sells = get_sells(curr_positions, curr_price, curr_std)
            
            #do_updates
            for i in pos_changes.keys():
                curr_positions[i][1] = pos_changes[i]
            print(curr_positions)

            for ticker in sells:
                side, bid, n_contracts= curr_positions[ticker]
                trader.writerow([
                    dt.datetime.now().isoformat(),
                    ticker,
                    -n_contracts,
                    side,
                    bid,
                    0]
                )
                trades.flush()
                curr_positions.pop(ticker)

                cash += bid*n_contracts
                print("cash increase")
            
            #update_portfolio_value
            
            capital = cash + sum([item[1]*item[2] for item in curr_positions.values()])
            
            performer.writerow([dt.datetime.now().isoformat(), cash, capital])
            perform.flush()

            #exit positions at eod
            if dt.time(hour=15, minute=59) == dt.time(hour=dt.datetime.now().hour, minute=dt.datetime.now().minute):
                to_sell = list(curr_positions.keys())
                for ticker in to_sell:
                    side, bid, n_contracts= curr_positions[ticker]
                    trader.writerow([
                        dt.datetime.now().isoformat(),
                        ticker,
                        -n_contracts,
                        side,
                        bid,
                        0]
                    )
                    curr_positions.pop(ticker)
                    cash += bid*n_contracts
                capital = cash
                performer.writerow([dt.datetime.now().isoformat(), cash, capital])
                perform.flush()

            print("sleeping till minute")
            time.sleep(60 - (dt.datetime.now().second + (dt.datetime.now().microsecond+1)/1000000))
        if (60*(dt.datetime.now().hour)) + dt.datetime.now().minute >=960:
            tomorrow = dt.datetime.today() + dt.timedelta(days=1)
            if tomorrow.isoweekday() == 6:
                sleep_till_day = dt.datetime.today() + dt.timedelta(days=3)
                delta = (dt.datetime(sleep_till_day.year, sleep_till_day.month, sleep_till_day.day, 0, 0) - dt.datetime.now())
                print("sleeping till next monday")
                time.sleep(delta.seconds + delta.microseconds/1000000)
                
            else:
                delta = (dt.datetime(tomorrow.year, tomorrow.month, tomorrow.day, 0, 0) - dt.datetime.now())
                print("sleeping till next midnight")
                time.sleep(delta.seconds + delta.microseconds/1000000)
    else:
        if dt.datetime.now().isoweekday() == 6:
            monday = dt.datetime.now() + dt.timedelta(days=2)
            delta = (dt.datetime(monday.year, monday.month, monday.day, 0, 0) - dt.datetime.now())
            print("sleeping till monday")
            time.sleep(delta.seconds + delta.microseconds/1000000)
        else:
            monday = dt.datetime.now() + dt.timedelta(days=1)
            delta = (dt.datetime(monday.year, monday.month, monday.day, 0, 0) - dt.datetime.now())
            print("sleeping till monday")
            time.sleep(delta.seconds + delta.microseconds/1000000)



        
        
