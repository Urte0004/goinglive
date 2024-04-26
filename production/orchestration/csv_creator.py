#if your csvs are not already defined with some entries

import csv
import datetime as dt
with open("production/portfolio/performance.csv", "w") as f:
    writer_thing = csv.writer(f)
    writer_thing.writerow(["datetime", "cash", "capital"])
    writer_thing.writerow([dt.datetime.now().isoformat(), 100000, 100000])
    f.flush()
with open("production/portfolio/trades.csv", "w") as f:
    writer_thing = csv.writer(f)
    writer_thing.writerow(["datetime","ticker","n_contracts","side","curr_ask","ev"])
    f.flush()
