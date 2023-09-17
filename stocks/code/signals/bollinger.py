import pandas as pd

def bollinger(df: pd.DataFrame, entry_datetime: int):
    # select only rows before entry_datetime
    df = df[df["open_time"] < entry_datetime]
    df["close"] = pd.to_numeric(df["close"])
    df["open_time"] = pd.to_datetime(df["open_time"], unit="ms")
    df["bollinger_upper"] = df["close"].rolling(16).mean() + 1.618 * df["close"].rolling(16).std()
    df["bollinger_lower"] = df["close"].rolling(16).mean() - 1.618 * df["close"].rolling(16).std()
    df = df.dropna()
    
    if df.iloc[-1]["close"] > df.iloc[-1]["bollinger_lower"] and df.iloc[-2]["close"] < df.iloc[-2]["bollinger_lower"]:
        take_profit = (df.iloc[-1]["bollinger_upper"] + df.iloc[-1]["bollinger_lower"]) / 2
        stop_loss = df.iloc[-1]["close"] - (take_profit - df.iloc[-1]["close"])
        ret_val = [
            take_profit,
            stop_loss,
            60 * 60,
            True
        ]
        return ret_val
    else:
        return None