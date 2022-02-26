import pandas as pd
import ccxt, datetime
import matplotlib.pyplot as plt

def data(symbol: str, limit: int, timeframe: str) -> pd.DataFrame:
    data = []
    exchange = ccxt.binance()
    ohlcv = exchange.fetch_ohlcv(symbol=symbol, limit=limit, timeframe=timeframe)

    for i in ohlcv:
        dt = datetime.datetime.utcfromtimestamp(i[0] / 1000)
        i.pop(0)
        i.insert(0, dt.strftime('%Y-%m-%d %H:%M'))
        data.append(i)

    df = pd.DataFrame(data, columns=["date", "open", "high", "low", "close", f"Volume {symbol}"])

    return df

def plot(df):
    plt.plot(df['date'], df['close'])
    plt.bar(df['date'], df['Volume XRP'])

    plt.show()

if __name__ == '__main__':
    Data = data("ETH/USDT", 288, "5m")
    plot(Data)
    print(Data)

