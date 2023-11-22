from __future__ import absolute_import, division, print_function, unicode_literals

import datetime
import os.path
import sys

import backtrader as bt


class FixedSize(bt.Sizer):
    params = (("startingValue", 0),)

    def _getsizing(self, comminfo, cash, data, isbuy):
        # Buy with 10% of the available cash only if i have more value than in t0
        if self.strategy.broker.getvalue() >= self.params.startingValue:
            size = int(cash * 0.1 / data.close)
            if size > 0:
                return size
        # Buy with 5% of the available cash only if i have less value than in t0
        else:
            size = int(cash * 0.05 / data.close)
            if size > 0:
                return size


class TestStrategy(bt.Strategy):
    params = (
        ("periodSmaShortBuy", 10),
        ("periodSmaLongBuy", 20),
        ("periodSmaShortSell", 20),
        ("periodSmaLongSell", 40),
        ("stopBuyingAt", 1.0),
        ("buyTimerLimit", 0),
    )

    def log(self, txt, dt=None, doprint=False):
        if doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print("%s, %s" % (dt.isoformat(), txt))

    def __init__(self):
        # Starting value
        self.startingValue = self.broker.getvalue()

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None

        self.smaShort = bt.ind.SMA(period=self.params.periodSmaShortBuy)
        self.smaLong = bt.ind.SMA(period=self.params.periodSmaLongBuy)

        self.smaShortSell = bt.ind.SMA(period=self.params.periodSmaShortSell)
        self.smaLongSell = bt.ind.SMA(period=self.params.periodSmaLongSell)
        self.macd = bt.ind.MACD()

        self.rsi = bt.ind.RelativeMomentumIndex()

        # Crossover Lines
        self.crossoverBuy = bt.ind.CrossOver(self.smaShort, self.smaLong)
        self.crossoverSell = bt.ind.CrossOver(self.smaShortSell, self.smaLongSell)

        self.buyTimerLimit = self.params.buyTimerLimit
        self.timer = 0

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    "BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f"
                    % (order.executed.price, order.executed.value, order.executed.comm),
                    doprint=False,
                )

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:
                self.log(
                    "SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f"
                    % (order.executed.price, order.executed.value, order.executed.comm),
                    doprint=False,
                )

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log("Order Canceled/Margin/Rejected", doprint=False)

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log(
            "OPERATION PROFIT, GROSS %.2f, NET %.2f" % (trade.pnl, trade.pnlcomm),
            doprint=False,
        )

    def next(self):
        # If i sold very recently, dont buy.
        if self.timer > 0:
            self.timer = self.timer - 1

        buySignal = (
            self.startingValue / (1 / self.params.stopBuyingAt) < self.broker.getvalue()
            and self.timer <= 0
            and self.crossoverBuy[0] > 0
            and self.macd.macd[0] > self.macd.signal[0]
            and self.rsi[0] > 70
        )
        sellSignal = self.crossoverSell[0] < 0

        if buySignal:
            self.buy()
        elif sellSignal:
            self.close()
            self.timer = self.buyTimerLimit


if __name__ == "__main__":
    cerebro = bt.Cerebro()

    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    datapath = os.path.join(modpath, "datasets/orcl-1995-2014.txt")

    data = bt.feeds.YahooFinanceCSVData(
        dataname=datapath,
        fromdate=datetime.datetime(2000, 1, 1),
        todate=datetime.datetime(2000, 12, 31),
        reverse=False,
    )

    cerebro.adddata(data)

    cerebro.broker.setcash(10000.0)

    cerebro.addsizer(FixedSize, startingValue=cerebro.broker.getvalue())

    cerebro.broker.setcommission(commission=0.001)

    """     cerebro.optstrategy(
        TestStrategy,
        periodSmaShortBuy=range(5, 11),
        periodSmaLongBuy=range(15, 21),
        periodSmaShortSell=range(15, 21),
        periodSmaLongSell=range(35, 41),
        stopBuyingAt=0.5,
        buyTimerLimit=20,
    ) """

    cerebro.addstrategy(
        TestStrategy,
        periodSmaShortBuy=10,
        periodSmaLongBuy=20,
        periodSmaShortSell=20,
        periodSmaLongSell=40,
        stopBuyingAt=0.5,
        buyTimerLimit=20,
    )

    print("Starting Portfolio Value: %.2f" % cerebro.broker.getvalue())

    cerebro.run()

    print("Finishing Portfolio Value: %.2f" % cerebro.broker.getvalue())

    cerebro.plot()

"""     best_result = float("-inf")
    best_periodSmaShortBuy = -1
    best_periodSmaLongBuy = -1
    best_periodSmaShortSell = -1
    best_periodSmaLongSell = -1
    for cerebro_obj in cerebro.run(optreturn=False):
        for strategy in cerebro_obj:
            if strategy.broker.getvalue() > best_result:
                best_result = strategy.broker.getvalue()
                best_periodSmaShortBuy = strategy.params.periodSmaShortBuy
                best_periodSmaLongBuy = strategy.params.periodSmaLongBuy
                best_periodSmaShortSell = strategy.params.periodSmaShortSell
                best_periodSmaLongSell = strategy.params.periodSmaLongSell

            print(
                "(periodSmaShortBuy %2d) (periodSmaLongBuy %2d) (periodSmaShortSell %2d) (periodSmaLongSell %2d) Ending Value %.2f"
                % (
                    strategy.params.periodSmaShortBuy,
                    strategy.params.periodSmaLongBuy,
                    strategy.params.periodSmaShortSell,
                    strategy.params.periodSmaLongSell,
                    strategy.broker.getvalue(),
                ),
            )

    print(
        "(best_periodSmaShortBuy %2d) (best_periodSmaLongBuy %2d) (best_periodSmaShortSell %2d) (best_periodSmaLongSell %2d) Ending Value %.2f"
        % (
            best_periodSmaShortBuy,
            best_periodSmaLongBuy,
            best_periodSmaShortSell,
            best_periodSmaLongSell,
            best_result,
        ),
    ) """
