def get_bittrex_rates(self, queue, pairs):

    base = pairs['base']
    markets = pairs['markets']

    rates = dict()

    for market in markets:
        ticker = "{}-{}".format(base, market)
        symbol_info = self.get_ticker(ticker)

        price = symbol_info['result']['Last']
        symbol = "{}{}".format(market, base)

        rates[symbol] = price

    queue.put(rates)
