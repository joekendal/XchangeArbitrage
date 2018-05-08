def get_binance_rates(self, queue, pairs):

    base = pairs['base']
    markets = pairs['markets']

    rates = dict()

    for market in markets:
        ticker = "{}{}".format(market, base)
        symbol_info = self.get_symbol_ticker(symbol=ticker)
        rates[ticker] = symbol_info['price']

    queue.put(rates)
