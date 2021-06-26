# This script is an example of how to set up trailing stop orders
import Config
import alpaca_trade_api as tradeapi
from helpers import calculate_quantity

# Create access to Alpaca API
api = tradeapi.REST(Config.API_KEY, Config.SECRET_KEY, Config.API_URL, 'v2')

symbols = ['SPY', 'IWM', 'DIA']
for symbol in symbols:
    quote = api.get_last_quote(symbol)

    api.submit_order(
        symbol=symbol,
        side='buy',
        type='market',
        qty=calculate_quantity(quote.bidprice),
        time_in_force='day'
    )

    api.submit_order(
        symbol='IWM',
        side='sell',
        qty=1,
        time_in_force='day',
        type='trailing_stop',
        trail_price='0.75'
    )

    api.submit_order(
        symbol='DIA',
        side='sell',
        qty=1,
        time_in_force='day',
        type='trailing_stop',
        trail_percent='0.70'
    )
