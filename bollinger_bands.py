import sqlite3
import pandas as pd
import pytz
import tulipy
import Config
import datetime as dt
from datetime import date
import alpaca_trade_api as tradeapi
from alpaca_trade_api.rest import TimeFrame

# First thing we do is create a connection to our database
connection = sqlite3.connect(Config.DB_FILE)
connection.row_factory = sqlite3.Row  # instead of returning a tuple this will return a sqlite object
# new connection cursor to start querying our database:
cursor = connection.cursor()

cursor.execute("""
    select id from strategy where name = 'bollinger_bands'
""")

strategy_id = cursor.fetchone()['id']

cursor.execute("""
    select symbol, name
    from stock
    join stock_strategy on stock_strategy.stock_id = stock.id
    where stock_strategy.strategy_id = ?
""", (strategy_id,))

stocks = cursor.fetchall()
symbols = [stock['symbol'] for stock in stocks]

# SETTING UP TIME VARIABLES:
# Set a constant for UTC timezone
UTC = pytz.timezone('UTC')
current_date = date.today().isoformat()
start_minute_bar = f"{current_date}T13:30:00+00:00"  # Market open (8:30)
end_minute_bar = f"{current_date}T20:00:00+00:00"  # Market close (3:00)

api = tradeapi.REST(Config.API_KEY, Config.SECRET_KEY, Config.API_URL, 'v2')  # added v2 to include updates.
orders = api.list_orders(status='all', after=f"{current_date}T13:30:00Z")
existing_order_symbols = [order.symbol for order in orders if order.status != 'canceled']
messages = []

for symbol in symbols:
    minute_bars = api.get_bars(symbol, TimeFrame.Minute,
                               pd.Timestamp('now').date(),
                               pd.Timestamp('now').date(),
                               adjustment='raw'
                               ).df
    market_open_mask = (minute_bars.index >= start_minute_bar) & (minute_bars.index < end_minute_bar)
    market_open_bars = minute_bars.loc[market_open_mask]

    if len(market_open_bars) >= 20:

        closes = market_open_bars.close.values
        lower, middle, upper = tulipy.bbands(closes, 20, 2)

        current_candle = market_open_bars.iloc[-1]
        previous_candle = market_open_bars.iloc[-2]

        if current_candle.close > lower[-1] and previous_candle.close < lower[-2]:
            print(f"{symbol} closed above lower bollinger band")
            print(current_candle)
            if symbol not in existing_order_symbols:  # if we have not already bought a stock
                limit_price = current_candle.close
                candle_range = current_candle.high - current_candle.low
                print(f"placing order for {symbol} at {limit_price}")

                api.submit_order(
                    symbol=symbol,
                    side='buy',
                    type='limit',
                    qty='1',
                    time_in_force='day',
                    order_class='bracket',
                    limit_price=limit_price,
                    take_profit=dict(
                        limit_price=limit_price + (candle_range * 3),
                    ),
                    stop_loss=dict(
                        stop_price=previous_candle.low,
                    )
                )
            else:
                print(f"Already an order for {symbol}, skipping")