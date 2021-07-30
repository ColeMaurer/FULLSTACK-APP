import btalib
import Config
import backtrader as bt
import pandas
import tulipy
import sqlite3
from datetime import date, datetime, time, timedelta

import bollinger_bands


class BollingerBands(bt.Strategy):
    # Bollinger strat starts after 20 minute bars for tulipy lib
    params = (('period', 20),)

    # Initializing values
    def __init__(self):
        self.opening_range = 0
        self.current_candle_low = 0
        self.current_candle_high = 0
        self.current_candle_close = 0
        self.bought_today = False
        self.order = None
        bands = bt.indicators.BollingerBands(self.data, period=self.p.period)

    def log(self, txt, dt=None):
        if dt is None:
            dt = self.datas[0].datetime.datetime()

        print('%s, %s' % (dt, txt))

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        if order.status in [order.Completed]:
            order_details = f"{order.executed.price}, Cost: {order.executed.value}, Comm {order.executed.comm}"
            # Logging order status
            if order.isbuy():
                self.log(f"BUY EXECUTED, Price: {order_details}")
            else:  # Sell
                self.log(f"SELL EXECUTED, Price: {order_details}")

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None
    # "next" is where the strategy lives
    def next(self):
        current_bar_datetime = self.data.num2date(self.data.datetime[0])
        previous_bar_datetime = self.data.num2date(self.data.datetime[-1])
        # Don't think any of this group is needed.
        if current_bar_datetime.date() != previous_bar_datetime.date():
            self.current_candle_low = self.data.low[0]
            self.current_candle_high = self.data.high[0]
            self.current_candle_close = self.data.close[0]
            self.bought_today = False
        # Market hours
        start_minute_bar = time(9, 30, 0)
        # end_minute_bar = time(4, 0, 0)

        # Setting up data to be used by tulipy to calculate bollinger bands
        dt = datetime.combine(date.today(), start_minute_bar) + timedelta(minutes=self.p.period)
        opening_range_end_time = dt.time()

        if current_bar_datetime.time() >= start_minute_bar \
                and current_bar_datetime.time() < opening_range_end_time:
            # If we have 20 closing values (this number can be adjusted during strat refinement)
            # if len(market_open_bars) >= 20:
            closes = self.data.close
            # Tulipy library analysis to calculate lower, middle, and upper bollinger bands:
            lower = bt.indicators.BollingerBands(self.data, period=self.p.period).lines.lowerband
            middle = bollinger_bands.middle
            upper = bollinger_bands.upper
            current_candle = data.iloc[-1]
            previous_candle = data.iloc[-2]
            # Copied all of this from bollinger bands strat to define entry and exit points - much modification needed
            if current_candle.close > lower[-1] and previous_candle.close < lower[-2]:
            # closed above lower bollinger band")
                limit_price = current_candle.close
                candle_range = current_candle.high - current_candle.low
                if self.order:
                    return
                # Exit for a profit here (if close is greater than opening range high plus range)
                # May need to make limit_price et from above part of the self._____ class.
                if self.position and (self.data.close[0] > (limit_price + candle_range * 3)):
                    self.close()
                # Entry point here: If we close above the opening range high
                if current_candle.close > lower[-1] and previous_candle.close < lower[-2] and not self.position and not self.bought_today:
                    self.order = self.buy()
                    self.bought_today = True
                # Exit for a loss here (if close is less than opening range high minus range)
                if self.position and (self.data.close[0] < previous_candle.low):
                    self.order = self.close()
                # Liquidate all positions at the end of the day:
                if self.position and current_bar_datetime.time() >= time(15, 45, 0):
                    self.log("RUNNING OUT OF TIME - LIQUIDATING POSITION")
                    self.close()

    # Back trader runs 'next' for the length of the data feed, then runs this stop
    # This is where we can print the results of the test
    def stop(self):
        self.log('(Num Opening Bars %2d) Ending Value %.2f' %
                 (self.params.period, self.broker.getvalue()))

        if self.broker.getvalue() > 130000:
            self.log("*** BIG WINNER ***")

        if self.broker.getvalue() < 70000:
            self.log("*** MAJOR LOSER ***")


if __name__ == '__main__':
    conn = sqlite3.connect(Config.DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DISTINCT(stock_id) as stock_id FROM stock_price_minute
    """)
    stocks = cursor.fetchall()
    # For individual stock uncomment the following with the stock_id from the database:
    stocks = [{'stock_id': 39}]
    # Make sure the stock_id entered above is actually in the database!

    for stock in stocks:
        print(f"== Testing {stock['stock_id']} ==")

        cerebro = bt.Cerebro()
        cerebro.broker.setcash(100000.0)
        cerebro.addsizer(bt.sizers.PercentSizer, percents=95)

        dataframe = pandas.read_sql("""
            select datetime, open, high, low, close, volume
            from stock_price_minute
            where stock_id = :stock_id
            and strftime('%H:%M:%S', datetime) >= '09:30:00' 
            and strftime('%H:%M:%S', datetime) < '16:00:00'
            order by datetime asc
        """, conn, params={"stock_id": stock['stock_id']}, index_col='datetime', parse_dates=['datetime'])

        data = bt.feeds.PandasData(dataname=dataframe)

        cerebro.adddata(data)
        cerebro.addstrategy(BollingerBands)
        # Optimized strategy (cannot run plot when doing this):
        # Remember to comment out line 124
        # strats = cerebro.optstrategy(OpeningRangeBreakout, num_opening_bars=[15, 30, 60])

        cerebro.run()
        #cerebro.plot()
