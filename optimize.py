from __future__ import absolute_import, division, print_function, unicode_literals

import datetime
import os.path
import sys

import backtrader as bt
from strategy import MyStrategy, CarefulSizer


def optimize():
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

    cerebro.optstrategy(
        MyStrategy,
        periodSmaShortBuy=range(5, 11),
        periodSmaLongBuy=range(15, 21),
        periodSmaShortSell=range(15, 21),
        periodSmaLongSell=range(35, 41),
        stopBuyingAt=0.5,
        buyTimerLimit=20,
    )

    best_result = float("-inf")
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
    )
