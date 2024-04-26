with open("production/portfolio/performance.csv", "r") as f:
    last = ''
    for line in f:
        last = line
    line = list(last.split(","))
    print(line)