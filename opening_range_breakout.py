# Opening range breakout Script: If a stock breaks out above of the first 15
# minute range, then we buy and expect it to go up further
import sqlite3
import Config
import datetime as dt
from datetime import date, time
import pandas as pd
import threading
import alpaca_trade_api as tradeapi
import time
from alpaca_trade_api.rest import TimeFrame
import smtplib, ssl
import pytz

# Email setup
context = ssl.create_default_context()

#First thing we do is create a connection to our database
connection = sqlite3.connect(Config.DB_FILE)
connection.row_factory = sqlite3.Row #instead of returning a tuple this will return a sqlite object
#new connection cursor to start querering our database:
cursor = connection.cursor()

cursor.execute("""
    select id from strategy where name = 'opening_range_breakout'
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

current_date = date.today().isoformat()
start_minute_bar = f"{current_date} 09:30:00-04:00" # Market open       # Double check time zone
end_minute_bar = f"{current_date} 09:45:00-04:00" # 15 minutes later
#api = tradeapi.REST(Config.API_KEY, Config.SECRET_KEY, base_url=Config.API_URL)
api = tradeapi.REST(Config.API_KEY, Config.SECRET_KEY, Config.API_URL, 'v2') # added v2 to include updates.
orders = api.list_orders(status='all', limit=500, after=f"{current_date}T13:30:00Z")
#orders = api.list_orders()
existing_order_symbols = [order.symbol for order in orders]

messages = []

# Set a constant for UTC timezone
UTC = pytz.timezone('UTC')

# Get the current time, 15minutes, and 1 hour ago
time_now = dt.datetime.now(tz=UTC)
time_15_min_ago = time_now - dt.timedelta(minutes=15)
time_1_hr_ago = time_now - dt.timedelta(hours=1)

for symbol in symbols:
    # Use the following once the alpaca account has been funded and polygon is accessible:
    #minute_bars = api.polygon.historic_agg_v2(symbol, 1, 'minute', _from=current_date, to=current_date).df
    #minute_bars = api.get_bars(symbol, TimeFrame.Minute,        # This comes from the alpaca example: long-short.py
        #                          pd.Timestamp('now').date(),
        #                          pd.Timestamp('now').date(), limit=1,
        #                          adjustment='raw')

# Get data from previous hour
# If using the Free plan, the latest one can fetch is 15 minutes ago
    minute_bars = api.get_bars(symbol, TimeFrame.Minute,
                                start=time_1_hr_ago.isoformat(),
                                end=time_15_min_ago.isoformat(),
                                adjustment='raw'
                                ).df

    opening_range_mask = (minute_bars.index >= start_minute_bar) & (minute_bars.index < end_minute_bar)
    opening_range_bars = minute_bars.loc[opening_range_mask]
    opening_range_low = opening_range_bars['low'].min()
    opening_range_high = opening_range_bars['high'].max()
    opening_range = opening_range_high - opening_range_low

    after_opening_range_mask = minute_bars.index >= end_minute_bar
    after_opening_range_bars = minute_bars.loc[after_opening_range_mask]

    after_opening_range_breakout = after_opening_range_bars[after_opening_range_bars['close'] > opening_range_high]
    #print("Made it to line 85!")
    if not after_opening_range_breakout.empty: # if we have breakout candidates
        #print("We have breakout candidates?")
        if symbol not in existing_order_symbols: # if we have not already bought a stock
            #print("No orders yet")
            limit_price = after_opening_range_breakout.iloc[0]['close']
            messages.append(f"placing order for {symbol} at {limit_price}, closed above {opening_range_high}\n\n{after_opening_range_breakout.iloc[0]}\n\n")
            print(f"placing order for {symbol} at {limit_price}, closed above {opening_range_high} at {after_opening_range_breakout.iloc[0]}")

            api.submit_order(
                symbol=symbol,
                side='buy',
                type='limit',
                qty='1',
                time_in_force='day',
                order_class='bracket',
                limit_price=limit_price,
                take_profit=dict(
                    limit_price=limit_price + opening_range,
                ),
                stop_loss=dict(
                    stop_price=limit_price - opening_range,
                )
            )
        else:
            print(f"Already an order for {symbol}, skipping")
print(messages)
#print("No breakout candidates determined")
#with smtplib.SMTP_SSL(Config.EMAIL_HOST, Config.EMAIL_PORT, context=context) as server:
#    server.login(Config.EMAIL_ADDRESS, Config.EMAIL_PASSWORD)
#
#    email_message = f"Subject: Trade Notifications for {current_date}\n\n"
#    email_message += "\n\n".join(messages)
#
#    server.sendmail(Config.EMAIL_ADDRESS, Config.EMAIL_ADDRESS, email_message)
#    server.sendmail(Config.EMAIL_ADDRESS, Config.EMAIL_SMS, email_message)
