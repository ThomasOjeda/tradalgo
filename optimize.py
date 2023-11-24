from strategy import MyStrategy


def optimize(
    cerebro,
    periodSmaShortBuy,
    periodSmaLongBuy,
    periodSmaShortSell,
    periodSmaLongSell,
    stopBuyingAt,
    buyTimerLimit,
    printLog,
):
    cerebro.optstrategy(
        MyStrategy,
        periodSmaShortBuy=periodSmaShortBuy,
        periodSmaLongBuy=periodSmaLongBuy,
        periodSmaShortSell=periodSmaShortSell,
        periodSmaLongSell=periodSmaLongSell,
        stopBuyingAt=stopBuyingAt,
        buyTimerLimit=buyTimerLimit,
        printLog=printLog,
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
