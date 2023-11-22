from __future__ import absolute_import, division, print_function, unicode_literals

import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])

# Import the backtrader platform
import backtrader as bt


# Create a Stratey
class TestStrategy(bt.Strategy):
    params = (("maperiodShort", 19), ("maperiodLong", 17))

    def log(self, txt, dt=None, doprint=False):
        """Logging function fot this strategy"""
        if doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print("%s, %s" % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None

        self.ema1 = bt.ind.EMA(period=3)
        self.ema2 = bt.ind.EMA(period=7)
        self.rsi = bt.ind.RSI(period=14)
        self.macd = bt.ind.MACD()

        # Create crossover signals
        self.crossover = bt.ind.CrossOver(self.ema1, self.ema2)
        self.macd_cross = bt.ind.CrossOver(self.macd.macd, self.macd.signal)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    "BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f"
                    % (order.executed.price, order.executed.value, order.executed.comm)
                )

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:  # Sell
                self.log(
                    "SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f"
                    % (order.executed.price, order.executed.value, order.executed.comm)
                )

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log("Order Canceled/Margin/Rejected")

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log("OPERATION PROFIT, GROSS %.2f, NET %.2f" % (trade.pnl, trade.pnlcomm))

    def next(self):
        # Check if we are in the market
        # Check for buy signal

        if self.crossover[0] > 0 and self.macd_cross[0] > 0:
            # Buy with 10% of the available cash
            size = int(self.broker.getcash() * 0.1 / self.data.close)
            self.buy(size=size)

        else:
            # Check for sell signal
            if self.crossover[0] < 0:
                # Sell all the shares
                self.close()


if __name__ == "__main__":
    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add a strategy
    cerebro.addstrategy(TestStrategy)

    # Datas are in a subfolder of the samples. Need to find where the script is
    # because it could have been called from anywhere
    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    datapath = os.path.join(modpath, "datasets/orcl-1995-2014.txt")

    # Create a Data Feed
    data = bt.feeds.YahooFinanceCSVData(
        dataname=datapath,
        # Do not pass values before this date
        fromdate=datetime.datetime(2000, 1, 1),
        # Do not pass values before this date30
        todate=datetime.datetime(2000, 12, 31),
        # Do not pass values after this date
        reverse=False,
    )

    # Add the Data Feed to Cerebro
    cerebro.adddata(data)

    # Set our desired cash start    cerebro.plot()

    cerebro.broker.setcash(10000.0)

    # Add a FixedSize sizer according to the stake
    cerebro.addsizer(bt.sizers.FixedSize, stake=10)

    # Set the commission
    cerebro.broker.setcommission(commission=0.001)

    # Print out the starting conditions
    print("Starting Portfolio Value: %.2f" % cerebro.broker.getvalue())

    # Run over everything

    cerebro.run()

    print("Finishing Portfolio Value: %.2f" % cerebro.broker.getvalue())

    cerebro.plot()

    """  
    best_result = float("-inf")
    best_short = -1
    best_long = -1

    for cerebro_obj in cerebro.run(optreturn=False):
        for strategy in cerebro_obj:
            if strategy.broker.getvalue() > best_result:
                best_result = strategy.broker.getvalue()
                best_short = strategy.params.maperiodShort
                best_long = strategy.params.maperiodLong

            print(
                "(MA PeriodShort %2d) (MA PeriodLong %2d) Ending Value %.2f"
                % (
                    strategy.params.maperiodShort,
                    strategy.params.maperiodLong,
                    strategy.broker.getvalue(),
                ),
            )

    print(
        "The best strategy was with SHORT:%2d LONG:%2d ENDING: %.2f"
        % (best_short, best_long, best_result)
    )
 """
