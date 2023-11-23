import datetime
import os.path
import sys

import backtrader as bt

from run import run
from optimize import optimize
from strategy import CarefulSizer

if __name__ == "__main__":
    cerebro = bt.Cerebro()

    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    datapath = os.path.join(modpath, "datasets/orcl-1995-2014.txt")

    data = bt.feeds.YahooFinanceCSVData(
        dataname=datapath,
        fromdate=datetime.datetime(1999, 1, 1),
        todate=datetime.datetime(2001, 12, 31),
        reverse=False,
    )

    cerebro.adddata(data)

    cerebro.broker.setcash(10000.0)

    cerebro.addsizer(CarefulSizer, startingValue=cerebro.broker.getvalue())

    cerebro.broker.setcommission(commission=0.001)

    """     run(
        cerebro,
        periodSmaShortBuy=10,
        periodSmaLongBuy=20,
        periodSmaShortSell=20,
        periodSmaLongSell=40,
        stopBuyingAt=0.5,
        buyTimerLimit=20,
    ) """
    optimize(
        cerebro,
        periodSmaShortBuy=range(5, 11),
        periodSmaLongBuy=range(15, 21),
        periodSmaShortSell=range(15, 21),
        periodSmaLongSell=range(35, 41),
        stopBuyingAt=0.5,
        buyTimerLimit=20,
    )
