A proprietary (but probably not succesful) statistical arbitrage trading strategy exploiting mispricings on Kalshi's INX (SP500)
event series. This is a project that live-tests this strategy: paper trades the strategy against real time SP500 prices and Kalshi
market prices and records portfolio statistics to csv files. The strategy assumes the SP500 index is a markov process, with 
mean = 0 (open price). Returns are then normally distributed, and integrating over this density function gives us a probability of
closing within a range.

We hope to implement this strategy with real money, after a significant testing period.
