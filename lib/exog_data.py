import yfinance as yf
import pandas as pd
from datetime import timedelta


def get_yfinance_data(
    ticker_symbol: str,
    date_interval: list[str, str],
    name: str,
    interval: str = "1d"

):
    ticker = yf.Ticker(ticker_symbol)
    df = ticker.history(
        start=date_interval[0], end=date_interval[1], interval=interval)[["Close"]]
    df.reset_index(inplace=True)
    df.columns = ["dates", f"{name}_close"]
    df["dates"] = df["dates"].dt.strftime("%Y-%m-%d")
    df["dates"] = pd.to_datetime(df["dates"])
    df["dates"] = df["dates"].apply(lambda x: x + timedelta(days=1))

    return df
