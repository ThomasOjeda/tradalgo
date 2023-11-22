from __future__ import absolute_import, division, print_function, unicode_literals

import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])

# Import the backtrader platform
import backtrader as bt


class FixedSize(bt.Sizer):
    params = (("startingValue", 0),)

    def _getsizing(self, comminfo, cash, data, isbuy):
        # Buy with 10% of the available cash only if i have more value than t0
        if self.strategy.broker.getvalue() >= self.params.startingValue:
            size = int(cash * 0.1 / data.close)
            if size > 0:
                print("buying 10%", size)
                return size
        # Buy with 5% of the available cash only if i have less value than t0
        else:
            size = int(cash * 0.05 / data.close)
            if size > 0:
                print("buying 5%", size)
                return size


# Create a Stratey
class TestStrategy(bt.Strategy):
    params = (("maperiodShort", 10), ("maperiodLong", 15), ("RSIperiod", 14))

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

        self.ema1 = bt.ind.SMA(period=6)
        self.ema2 = bt.ind.SMA(period=15)
        self.macd = bt.ind.MACD()

        # Create crossover signals
        self.crossover = bt.ind.CrossOver(self.ema1, self.ema2)

        self.macd_cross = bt.ind.CrossOver(self.macd.macd, self.macd.signal)

        # Create the morningstar indicator
        self.ms = bt.talib.CDLMORNINGSTAR(
            self.data.open,
            self.data.high,
            self.data.low,
            self.data.close,
            penetration=0.1,
        )
        self.timeTillNextBuy = 1

        # Create crossover signals
        # self.crossover = bt.ind.CrossOver(self.ema1, self.sma2)
        # self.rsicrossup = bt.ind.CrossUp(self.rsi, bt.LineNum(70))
        # self.rsicrossdown = bt.ind.CrossDown(self.rsi, bt.LineNum(30))

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
                    % (order.executed.price, order.executed.value, order.executed.comm),
                    doprint=True,
                )

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:  # Sell
                self.log(
                    "SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f"
                    % (order.executed.price, order.executed.value, order.executed.comm),
                    doprint=True,
                )

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log("Order Canceled/Margin/Rejected", doprint=True)

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log(
            "OPERATION PROFIT, GROSS %.2f, NET %.2f" % (trade.pnl, trade.pnlcomm),
            doprint=True,
        )

    def next(self):
        # Define the buy and sell conditions
        buySignal = self.crossover[0] > 0 and self.macd.macd[0] > self.macd.signal[0]
        sellSignal = self.crossover[0] < 0 and (
            self.macd_cross[0] < 0
            or self.macd_cross[-1] < 0
            or self.macd_cross[-2] < 0
            or self.macd_cross[-3] < 0
        )

        # Check if we are in the market
        if not self.position:
            # If not, check if we should enter
            if buySignal:
                self.buy()
            elif sellSignal:
                self.sell()
        else:
            # If we are in the market, check if we should exit
            if self.position.size > 0 and sellSignal:
                # Close the long position
                self.close()
            elif self.position.size < 0 and buySignal:
                # Close the short position
                self.close()


if __name__ == "__main__":
    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add a strategy
    cerebro.addstrategy(TestStrategy)
    """ ,
        maperiodShort=range(2, 10),
        maperiodLong=range(11, 20),
        RSIperiod=range(14, 20), """

    # Datas are in a subfolder of the samples. Need to find where the script is
    # because it could have been called from anywhere
    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    datapath = os.path.join(modpath, "datasets/orcl-1995-2014.txt")

    # Create a Data Feed
    data = bt.feeds.YahooFinanceCSVData(
        dataname=datapath,
        # Do not pass values before this date
        fromdate=datetime.datetime(1999, 1, 1),
        # Do not pass values before this date30
        todate=datetime.datetime(2000, 12, 31),
        # Do not pass values after this date
        reverse=False,
    )

    # Add the Data Feed to Cerebro
    cerebro.adddata(data)

    # Set our desired cash start

    cerebro.broker.setcash(10000.0)

    # Add a FixedSize sizer according to the stake
    cerebro.addsizer(FixedSize, startingValue=cerebro.broker.getvalue())

    # Set the commission
    cerebro.broker.setcommission(commission=0.001)

    # Print out the starting conditions
    print("Starting Portfolio Value: %.2f" % cerebro.broker.getvalue())

    # Run over everything

    cerebro.run()

    print("Finishing Portfolio Value: %.2f" % cerebro.broker.getvalue())

    cerebro.plot()

"""     best_result = float("-inf")
    best_short = -1
    best_long = -1
    best_rsi = -1
    for cerebro_obj in cerebro.run(optreturn=False):
        for strategy in cerebro_obj:
            if strategy.broker.getvalue() > best_result:
                best_result = strategy.broker.getvalue()
                best_short = strategy.params.maperiodShort
                best_long = strategy.params.maperiodLong
                best_rsi = strategy.params.RSIperiod
            print(
                "(MA PeriodShort %2d) (MA PeriodLong %2d) (RSIperiod %2d) Ending Value %.2f"
                % (
                    strategy.params.maperiodShort,
                    strategy.params.maperiodLong,
                    strategy.params.RSIperiod,
                    strategy.broker.getvalue(),
                ),
            )

    print(
        "The best strategy was with SHORT:%2d LONG:%2d RSI:%2d ENDING: %.2f"
        % (best_short, best_long, best_rsi, best_result)
    ) """
