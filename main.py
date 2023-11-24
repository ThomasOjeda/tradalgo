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
        fromdate=datetime.datetime(1997, 1, 1),
        todate=datetime.datetime(2002, 12, 31),
        reverse=False,
    )

    cerebro.adddata(data)

    cerebro.broker.setcash(10000.0)

    cerebro.addsizer(CarefulSizer, startingValue=cerebro.broker.getvalue())

    cerebro.broker.setcommission(commission=0.001)

    run(
        cerebro,
        periodSmaShortBuy=5,
        periodSmaLongBuy=35,
        periodSmaShortSell=45,
        periodSmaLongSell=190,
        stopBuyingAt=0.5,
        buyTimerLimit=20,
        printLog=True,
    )
    """ optimize(
        cerebro,
        periodSmaShortBuy=(5, 10, 15, 20, 25, 30),
        periodSmaLongBuy=(35, 40, 45, 50, 55, 60, 65),
        periodSmaShortSell=(40, 45, 50, 55, 60, 65, 70),
        periodSmaLongSell=(185, 190, 195, 200, 205, 210, 215),
        stopBuyingAt=0.5,
        buyTimerLimit=20,
        printLog=False,
    ) """
