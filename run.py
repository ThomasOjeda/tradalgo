from __future__ import absolute_import, division, print_function, unicode_literals

import datetime
import os.path
import sys

import backtrader as bt

from strategy import MyStrategy, CarefulSizer


def run():
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

    cerebro.addsizer(CarefulSizer, startingValue=cerebro.broker.getvalue())

    cerebro.broker.setcommission(commission=0.001)

    cerebro.addstrategy(
        MyStrategy,
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
