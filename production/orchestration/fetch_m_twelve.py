import datetime as dt
import pandas as pd
import numpy as np
import requests


def fetch(key, stock_ticker, today, std):
    twelve_response = requests.get(f"https://api.twelvedata.com/time_series?apikey={key}&interval=1min&symbol={stock_ticker}&previous_close=true&outputsize=1").json()
    twelve_response = twelve_response["values"]
    curr_price = float(twelve_response[0]["close"])
    mins_till_close = (dt.datetime.combine(date=today, time=dt.time(hour=16, minute=0))-dt.datetime.now()).total_seconds()/60
    curr_std = np.sqrt(mins_till_close)*std
    return curr_price, curr_std