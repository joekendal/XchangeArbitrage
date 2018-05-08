from multiprocessing import Process, Queue

from binance.client import Client
from bittrex.bittrex import Bittrex

from API.Binance import *
from API.Bittrex import *

BINANCE_API_KEY = ""
BINANCE_API_SECRET = ""

BITTREX_API_KEY = ""
BITTREX_API_SECRET = ""

PAIRS = {
    'base': 'ETH',
    'markets': ['XRP', 'XLM', 'DASH', 'LTC'],
}

class ArbitrageBot:

    def __init__(self, BinanceClient, BittrexClient, Pairs):
        self.binance = BinanceClient
        self.bittrex = BittrexClient
        self.pairs = Pairs
        self.rates = dict()
        self.discrepancies = list()
        self.orders = list()

    def get_exchange_rates(self):
        binance_rates = Queue()
        bittrex_rates = Queue()

        p1 = Process(target=self.binance.get_binance_rates, args=(binance_rates, self.pairs))
        p1.start()
        p2 = Process(target=self.bittrex.get_bittrex_rates, args=(bittrex_rates, self.pairs))
        p2.start()

        p1.join()
        binance_rates = binance_rates.get()
        p2.join()
        bittrex_rates = bittrex_rates.get()

        self.rates = {
            'exchanges': {'binance': binance_rates, 'bittrex': bittrex_rates},
        }

    def get_discrepancies(self):

        for symbol, price in self.rates['exchanges']['binance'].items():
            difference = float(price) - float(self.rates['exchanges']['bittrex'][symbol])
            difference = abs(difference)
            if difference != 0.00000000:
                discrepancy = {
                    'ticker': symbol,
                    'binance': float(price),
                    'bittrex': float(self.rates['exchanges']['bittrex'][symbol])
                }
                self.discrepancies.append(discrepancy)

    def configure_trades(self):

        for discrepancy in self.discrepancies:
            ticker = discrepancy['ticker']
            binance_price = discrepancy['binance']
            bittrex_price = discrepancy['bittrex']

            if binance_price > bittrex_price:
                order = {
                    'buy': ticker,
                    'from': 'bittrex',
                    'buy_price': bittrex_price,
                    'sell': ticker,
                    'to': 'binance',
                    'sell_price': binance_price,
                }
                self.orders.append(order)

            elif binance_price < bittrex_price:
                order = {
                    'buy': ticker,
                    'from': 'binance',
                    'buy_price': binance_price,
                    'sell': ticker,
                    'to': 'bittrex',
                    'sell_price': bittrex_price,
                }
                self.orders.append(order)

    def print_discrepancies(self):

        for order in self.orders:

            percent_diff = round((((order['sell_price'] - order['buy_price'])/order['buy_price']) * 100), 2)

            if percent_diff > 0.25:
                print("{}:\n\t({} @ {}) <---- {}% ----> ({} @ {})\n".format((order['buy'][:-3] + "/" + order['buy'][-3:]), order['from'], order['buy_price'], percent_diff, order['to'], order['sell_price']))

    def execute_orders(self):
        pass

    def get_order_status(self):
        pass



def main():

    BinanceClient = Client(api_key=BINANCE_API_KEY, api_secret=BINANCE_API_SECRET)
    Client.get_binance_rates = get_binance_rates

    BittrexClient = Bittrex(None, None)
    Bittrex.get_bittrex_rates = get_bittrex_rates

    bot = ArbitrageBot(BinanceClient, BittrexClient, PAIRS)

  # while True:
    bot.get_exchange_rates()
    bot.get_discrepancies()
    bot.configure_trades()
    bot.print_discrepancies()
    # bot.execute_orders()


if __name__ == "__main__":
    main()
