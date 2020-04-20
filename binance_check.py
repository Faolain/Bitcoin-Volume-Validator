from volumne_analyser import VolumeAnalyser

import argparse
from pprint import pprint

from binance.client import Client
from binance.websockets import BinanceSocketManager



def main():
    def process_message(msg):
        # Is a order book entry 
        if 'A' in msg:
            data = {
                'u' : int(msg['u']), # Unique, order book updateId
                'bb': float(msg['b']),  # best bid 
                'bo': float(msg['a']), # best offer
                'bq': float(msg['B']), # best bid qty
                'aq': float(msg['A']), # best ask qty
            }
            va.process_book_entry(data)

        # Is a trade stream update 
        else:
            data = { 
                'ts': msg['T'],
                'price': float(msg['p']),
                'qty': float(msg['q']),
            }
            va.process_trade_entry(data) 
            va.print_summary()


    bm = BinanceSocketManager(client)
    # Real time book ticker stream
    # https://github.com/binance-exchange/binance-official-api-docs/blob/master/web-socket-streams.md#individual-symbol-book-ticker-streams
    # https://github.com/sammchardy/python-binance/blob/c66695a785e8d3cf0975d09b624f79772dac4115/binance/websockets.py#L409

    bm.start_symbol_book_ticker_socket(va.symbol, process_message)
    # Real time trade execution feed
    # https://github.com/binance-exchange/binance-official-api-docs/blob/master/web-socket-streams.md#trade-streams
    # https://github.com/sammchardy/python-binance/blob/c66695a785e8d3cf0975d09b624f79772dac4115/binance/websockets.py#L254
    bm.start_trade_socket(va.symbol, process_message)
    bm.start()


if __name__ == "__main__":


    parser = argparse.ArgumentParser()
    parser.add_argument('-t','--ticker', help='Ticker', default='BTCUSDT')
    args = parser.parse_args()

    client = Client("DdEn5fpqEAekNJCVYmflOY9pLfIozLTjU4qXm5HqB9vyFh9PAB7LNdBWPjrkHf43", "c5NjpuJPGYgQZ60ZUXE3z6FQTV3YVOTNVz5JZ5aW2ST3uTJM65mykaFjCDMhPa1D")
    exinfo = client.get_exchange_info()
    symbol_hashes = {} 
    for s in exinfo['symbols']:
        symbol_hashes[s['symbol']] = { 
            'symbol': s['symbol'],
            'base_asset': s['baseAsset'],
            'quote_asset': s['quoteAsset'],
        }

    if args.ticker not in symbol_hashes:
        raise SystemExit(args.ticker+' is an invalid binance ticker')


    global va 
    va = VolumeAnalyser('Binance' )
    va.set_symbol_info( symbol_hashes[args.ticker] ) 
    main()