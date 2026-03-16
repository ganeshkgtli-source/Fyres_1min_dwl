import pandas as pd


def convert_time(df):

    df["timestamp"] = (
        pd.to_datetime(df["timestamp"], unit="s", utc=True)
        .dt.tz_convert("Asia/Kolkata")
    )

    return df


def format_dataframe(df, symbol):

    df["SYMBOL"] = symbol.split(":")[1]

    df["TIME_FRAME"] = "1_MIN"

    df["DATE"] = pd.to_datetime(df["timestamp"]).dt.date

    df["TIME"] = pd.to_datetime(df["timestamp"]).dt.time

    df["TIME1"] = pd.to_datetime(df["TIME"], format="%H:%M:%S")

    df["DAY"] = (
        pd.to_datetime(df["timestamp"])
        .dt.day_name()
        .str.upper()
    )

    df["CANDLE_COUNT"] = df["TIME1"].apply(
        lambda t: 0 if t.strftime("%H:%M:%S") == "00:00:00"
        else int(
            (
                pd.Timedelta(t.strftime("%H:%M:%S"))
                - pd.Timedelta("09:15:00")
            ).total_seconds() // 60 + 1
        )
    )

    df["CATEGORY"] = "XX"

    df = df.rename(
        columns={
            "open": "OPEN",
            "high": "HIGH",
            "low": "LOW",
            "close": "CLOSE",
            "volume": "VOLUME",
        }
    )

    df["TOTAL_VOLUME"] = df.groupby("DATE")["VOLUME"].cumsum()

    df = df[
        [
            "DATE",
            "DAY",
            "TIME_FRAME",
            "CATEGORY",
            "SYMBOL",
            "CANDLE_COUNT",
            "TIME",
            "OPEN",
            "HIGH",
            "LOW",
            "CLOSE",
            "VOLUME",
            "TOTAL_VOLUME",
        ]
    ]

    return df