from strategy import MyStrategy


def run(
    cerebro,
    periodSmaShortBuy,
    periodSmaLongBuy,
    periodSmaShortSell,
    periodSmaLongSell,
    stopBuyingAt,
    buyTimerLimit,
):
    cerebro.addstrategy(
        MyStrategy,
        periodSmaShortBuy=periodSmaShortBuy,
        periodSmaLongBuy=periodSmaLongBuy,
        periodSmaShortSell=periodSmaShortSell,
        periodSmaLongSell=periodSmaLongSell,
        stopBuyingAt=stopBuyingAt,
        buyTimerLimit=buyTimerLimit,
    )

    print("Starting Portfolio Value: %.2f" % cerebro.broker.getvalue())

    cerebro.run()

    print("Finishing Portfolio Value: %.2f" % cerebro.broker.getvalue())

    cerebro.plot()
