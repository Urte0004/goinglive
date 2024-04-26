def get_cash_and_capital(portfolio):
    last = ''
    for line in portfolio:
        last = line
    last = last.replace('\n', '')
    last = last.split(",")
    print(last)
    return float(last[1]), float(last[2])