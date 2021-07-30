# This strategy calculates the 200 day moving average for the s&p 500, goes long when
# the price crosses above the average and goes to cash when it crosses below

import Config
from datetime import date
import alpaca_trade_api as tradeapi
from alpaca_trade_api.rest import TimeFrame
import numpy
import pandas
import pandas_market_calendars as market_calendar
import tulipy
import math

# Getting last days of month, stock to trade
nyse = market_calendar.get_calendar('NYSE')
df = nyse.schedule(start_date='2020-01-01', end_date='2031-12-31')
df = df.groupby(df.index.strftime('%Y-%m')).tail(1)
df['date'] = pandas.to_datetime(df['market_open']).dt.date
last_days_of_month = [date.isoformat() for date in df['date'].tolist()]
symbol = 'SPY'

# Alpaca Account Info:
# ----------------------------------------------------------------------------- #
api = tradeapi.REST(Config.LIVE_API_KEY, Config.LIVE_SECRET_KEY, Config.LIVE_API_URL, 'v2')
# Get our account information.
account = api.get_account()
# Check if our account is restricted from trading.
if account.trading_blocked:
    print('Account is currently restricted from trading.')
# Check how much money we can use to open new positions:
cash = float(account.buying_power)
# ----------------------------------------------------------------------------- #

# Gathering price data:
barsets = api.get_bars(symbol, TimeFrame.Day, start='2020-01-01', end=date.today().isoformat(), adjustment='raw')
recent_closes = [bar.c for bar in barsets]
print(f"processing symbol {symbol}")
bar_date = [bar.t.date().isoformat() for bar in barsets]
todays_date = date.today().isoformat()
print(recent_closes[-1])
quantity = math.floor(cash / (recent_closes[-1]))
print(f"Quantity to buy: {quantity}")

for bar in barsets:
    if todays_date == bar_date:
        if todays_date in last_days_of_month:
            sma_200 = tulipy.sma(numpy.array(recent_closes), period=200)
            print(sma_200[-1])
            if recent_closes[-1] > sma_200[-1]:
                # Check if we already have an order:
                # Unless we don't care about old orders? All in on SPY baby!!
                api.submit_order(
                    symbol=symbol,
                    side='buy',
                    type='market',
                    qty=quantity,
                    time_in_force='day',
                )
            elif recent_closes < sma_200:
                # Bail! Go back to holding cash.
                api.close_all_positions()
        else:
            print("Today is not the end of the month!")