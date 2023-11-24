import backtrader as bt


class CarefulSizer(bt.Sizer):
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


class MyStrategy(bt.Strategy):
    params = (
        ("periodSmaShortBuy", 20),
        ("periodSmaLongBuy", 40),
        ("periodSmaShortSell", 50),
        ("periodSmaLongSell", 200),
        ("stopBuyingAt", 1.0),
        ("buyTimerLimit", 0),
        ("printLog", True),
    )

    def log(self, txt, dt=None):
        if self.params.printLog:
            dt = dt or self.datas[0].datetime.date(0)
            print("%s, %s" % (dt.isoformat(), txt))

    def __init__(self):
        # Starting value
        self.startingValue = self.broker.getvalue()

        self.smaShortBuy = bt.ind.SMA(period=self.params.periodSmaShortBuy)
        self.smaLongBuy = bt.ind.SMA(period=self.params.periodSmaLongBuy)

        self.smaShortSell = bt.ind.SMA(period=self.params.periodSmaShortSell)
        self.smaLongSell = bt.ind.SMA(period=self.params.periodSmaLongSell)
        self.macd = bt.ind.MACD()

        self.rsi = bt.ind.RSI()

        # Crossover Lines
        self.crossoverBuy = bt.ind.CrossOver(self.smaShortBuy, self.smaLongBuy)
        self.crossoverSell = bt.ind.CrossOver(self.smaShortSell, self.smaLongSell)

        self.timer = 0

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    "BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f"
                    % (order.executed.price, order.executed.value, order.executed.comm)
                )

            else:
                self.log(
                    "SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f"
                    % (order.executed.price, order.executed.value, order.executed.comm)
                )

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log("Order Canceled/Margin/Rejected")

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log("OPERATION PROFIT, GROSS %.2f, NET %.2f" % (trade.pnl, trade.pnlcomm))

    def next(self):
        # If i sold very recently, dont buy.
        if self.timer > 0:
            self.timer = self.timer - 1

        buySignal = (
            self.startingValue / (1 / self.params.stopBuyingAt) < self.broker.getvalue()
            and self.timer <= 0
            and self.crossoverBuy[0] > 0
            and self.macd.macd[0] > self.macd.signal[0]
            and self.rsi[0] < 70
        )

        sellSignal = (
            self.crossoverSell[0] < 0 and self.macd.macd[0] < self.macd.signal[0]
        )

        if buySignal:
            self.buy()
        elif sellSignal:
            self.close()
            self.timer = self.params.buyTimerLimit
