import pandas_ta as ta
from ccxt_data import data, pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_finance import candlestick_ohlc
from matplotlib.collections import LineCollection

# Styling the Chart.
plt.style.use('seaborn-dark')

for param in ['figure.facecolor', 'axes.facecolor', 'savefig.facecolor']:
    plt.rcParams[param] = '#131722'  # bluish dark grey
for param in ['text.color', 'axes.labelcolor', 'xtick.color', 'ytick.color']:
    plt.rcParams[param] = '0.9'  # very light grey


class GridTradingSystem:
    def __init__(self, symbol: str, df: pd.DataFrame, yesterdays_price: pd.DataFrame, length: int):
        self.symbol = symbol
        self.length = length
        self.df = df
        self.yesterdays_price = yesterdays_price

        self.df["MA"] = ta.dema(self.df['close'], length=9)

        self.levels = []

        self.cash, self.trade_amount, self.depot = 100, 0.018, 0

        self.buy, self.buy_date = [], []
        self.sell, self.sell_date = [], []
        self.buy_levels = []

    # Calculate the Grid Levels and save them in a list.
    def grid(self):
        diff = (self.yesterdays_price['high'][0] - self.yesterdays_price['low'][0])

        distance = diff / 5
        start = ((diff / 2) + self.yesterdays_price['low'][0]) - (distance * 6)

        for _ in range(11):
            start += distance
            self.levels.append(start)

    def strategy(self):
        for idx, close in enumerate(self.df['close']):
            if idx > 9:
                for i in range(11):
                    if round(self.levels[i]) == round(self.df['MA'][idx]):
                        if self.levels[i] < self.df['close'][idx - 3]:
                            if self.cash > self.trade_amount * close:
                                self.depot += self.trade_amount
                                self.cash -= self.trade_amount * close
                                self.buy.append(close)
                                self.buy_date.append(idx)
                                self.buy_levels.append(i)

                        elif self.levels[i] > self.df['close'][idx - 3]:
                            if len(self.buy_levels) > 0:
                                if self.depot > self.trade_amount:
                                    for buy_level in self.buy_levels:
                                        if buy_level < i:
                                            self.cash += (close * self.trade_amount)
                                            self.depot -= self.trade_amount
                                            self.sell.append(close)
                                            self.sell_date.append(idx)

                                            self.buy_levels.pop(self.buy_levels.index(buy_level))

        print(
            f"Total Balance: {self.df['close'].iloc[-1] * self.depot + self.cash}$, Depot: {self.depot}, Cash: {self.cash}$\nTrades: {len(self.buy) + len(self.sell)}")

    def plot(self):
        grid_length = []
        for i in self.levels:
            grid_length.append(list([i for _ in range(self.length)]))

        Y = np.array(grid_length)
        X = np.array([_ for _ in range(self.length)])

        x = np.tile(X, Y.shape[0]).reshape(*Y.shape)
        v = np.stack((x, Y), axis=-1)
        c = LineCollection(v)

        fig, ax = plt.subplots()
        ax.add_collection(c)
        ax.autoscale()
        self.df.drop(columns=['date', f'Volume {self.symbol}'])
        self.df['date'] = X
        candlestick_ohlc(ax, self.df.values, width=0.6, colorup='gray', colordown='y')
        ax.plot(self.df['MA'])
        ax.grid(color='#2A3459')
        ax.plot(self.buy_date, self.buy, 'v', c='g')
        ax.plot(self.sell_date, self.sell, 'v', c='r')

        plt.show()


def main():
    symbol = "ETH/USDT"
    length = 120
    df = data(symbol, length, "1h")
    yesterdays_price = data(symbol, 2, "1d")

    GTS = GridTradingSystem(symbol, df, yesterdays_price, length)
    GTS.grid()
    GTS.strategy()
    GTS.plot()


if __name__ == '__main__':
    main()
