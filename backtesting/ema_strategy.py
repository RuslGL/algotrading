import pandas as pd

from backtesting import Backtest
from backtesting import Strategy
from backtesting.lib import crossover

df = 'backtesting/data/btc_2023/bitcoin_trades_2023_1H.csv'


def EMA(values, n):
    ema_values = pd.Series(values).ewm(span=n, min_periods=n).mean()
    return ema_values


class EmaCross(Strategy):
    # Define the two MA lags as *class variables*
    # for later optimization
    n1 = 10
    n2 = 20

    def init(self):
        # Precompute the two moving averages
        self.ema1 = self.I(EMA, self.data.Close, self.n1)
        self.ema2 = self.I(EMA, self.data.Close, self.n2)

    def next(self):
        # If sma1 crosses above sma2, close any existing
        # short trades, and buy the asset
        if crossover(self.ema1, self.ema2):
            # self.position.close()
            self.buy()

        # Else, if sma1 crosses below sma2, close any existing
        # long trades, and sell the asset
        elif crossover(self.ema2, self.ema1):
            self.position.close()
            # self.sell()


df = pd.read_csv(df)

df.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
print(df.head())

df['Date'] = pd.to_datetime(df['Date'])
df = df.set_index('Date')
df.index.name = None
print(df.head())

df = df.dropna()

bt = Backtest(df, EmaCross, cash=10_000_000, commission=.001)
stats = bt.run()
print(stats)


new_stats = bt.optimize(n1=range(5, 30, 1),
                        n2=range(10, 150, 5),
                        maximize='Equity Final [$]',
                        constraint=lambda param: param.n1 < param.n2)
print(new_stats)
print(new_stats._strategy)
