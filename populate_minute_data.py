import Config
import sqlite3
import pandas as pd
import csv
import alpaca_trade_api as tradeapi
from alpaca_trade_api.rest import TimeFrame
from datetime import datetime, timedelta

connection = sqlite3.connect(Config.DB_FILE)
connection.row_factory = sqlite3.Row

cursor = connection.cursor()

api = tradeapi.REST(Config.API_KEY, Config.SECRET_KEY, Config.API_URL, 'v2')
symbols = []
stock_ids = {}

with open('qqq.csv') as f:
    reader = csv.reader(f)
    for line in reader:
        symbols.append(line[1])

cursor.execute("""
    SELECT * FROM stock
""")
stocks = cursor.fetchall()

for stock in stocks:
    symbol = stock['symbol']
    stock_ids[symbol] = stock['id']

for symbol in symbols:
    # Start and end dates of desired back testing range (here I am doing ~1 yr)
    start_date = datetime(2020, 1, 6).date()
    end_date_range = datetime(2020, 12, 20).date()

    while start_date < end_date_range:
        end_date = start_date + timedelta(days=4)

        print(f"=== Fetching minute bars {start_date}-{end_date} for {symbol}")
        minutes = api.get_bars(symbol, TimeFrame.Minute, start_date, end_date, adjustment='raw').df
        minutes_df = pd.DataFrame(minutes)
        # Forward filling with duplicate data in the case of missing bars:
        minutes_df = minutes_df.resample('1min').ffill()

        for index, row in minutes_df.iterrows():
            cursor.execute("""
                INSERT INTO stock_price_minute (stock_id, datetime, open, high, low, close, volume)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (stock_ids[symbol], index.tz_localize(None).isoformat(), row['open'], row['high'], row['low'], row['close'], row['volume']))

        start_date = start_date + timedelta(days=7)

connection.commit()