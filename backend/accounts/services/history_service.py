import pandas as pd
import time
import io
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

from accounts.services.fyers_client import get_fyers_client
from accounts.services.symbol_service import download_bse_symbols, get_filtered_symbols
from accounts.services.data_formatter import convert_time

from accounts.models import BhavcopyFile, OneMinDataFile


# =========================================================
# GET LAST SAVED DATE
# =========================================================

def get_last_saved_date(symbol):
    try:
        obj = OneMinDataFile.objects.filter(
            symbol=symbol,
            is_deleted=False
        ).first()

        if not obj:
            return None

        df = pd.read_csv(io.BytesIO(obj.file_data))

        if df.empty or "DATE" not in df.columns:
            return None

        df["DATE"] = pd.to_datetime(df["DATE"], errors="coerce")
        last_date = df["DATE"].max()

        if pd.isna(last_date):
            return None

        return last_date.date()

    except Exception as e:
        print(f"[{symbol}] READ ERROR:", e)
        return None


# =========================================================
# FORMAT DATAFRAME
# =========================================================

def format_dataframe(df, symbol):

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.dropna(subset=["timestamp"])

    df["SYMBOL"] = symbol
    df["TIME_FRAME"] = "1_MIN"

    df["DATE"] = df["timestamp"].dt.date
    df["TIME"] = df["timestamp"].dt.time
    df["DAY"] = df["timestamp"].dt.day_name().str.upper()

    market_open = 9 * 60 + 15

    def candle(ts):
        minutes = ts.hour * 60 + ts.minute
        diff = minutes - market_open
        return 0 if diff < 0 else diff + 1

    df["CANDLE_COUNT"] = df["timestamp"].apply(candle)

    df["CATEGORY"] = "XX"

    df = df.rename(columns={
        "open": "OPEN",
        "high": "HIGH",
        "low": "LOW",
        "close": "CLOSE",
        "volume": "VOLUME"
    })

    df["TOTAL_VOLUME"] = df.groupby("DATE")["VOLUME"].cumsum()
    df["SHARE_CHECK"] = ""

    return df


# =========================================================
# DATE RANGE CHUNKS
# =========================================================

def daterange_chunks(start, end, chunk=100):

    curr = start

    while curr <= end:
        next_date = min(curr + timedelta(days=chunk-1), end)
        yield curr, next_date
        curr = next_date + timedelta(days=1)


# =========================================================
# PROCESS SINGLE SYMBOL (PARALLEL SAFE)
# =========================================================

def process_symbol(symbol, client_id, end_date):

    # ✅ FIX 1: Separate fyers client per thread
    fyers = get_fyers_client(client_id)

    symbol_start = time.time()

    print(f"\n===================================")
    print(f"[{symbol}] Downloading")
    print(f"===================================")

    default_start = datetime(2018, 4, 1).date()
    last_saved = get_last_saved_date(symbol)

    if last_saved:
        start_date = last_saved + timedelta(days=1)
        print(f"[{symbol}] Resuming from:", start_date)
    else:
        start_date = default_start
        print(f"[{symbol}] Fresh download from:", start_date)

    if start_date > end_date:
        print(f"[{symbol}] Already up-to-date")
        return

    all_chunks = []
    rotation = 0
    first_valid_found = False
    empty_count = 0

    for chunk_start, chunk_end in daterange_chunks(start_date, end_date):

        print(f"[{symbol}] ROTATION {rotation} | {chunk_start} -> {chunk_end}")

        payload = {
            "symbol": symbol,
            "resolution": "1",
            "date_format": "1",
            "range_from": chunk_start.strftime("%Y-%m-%d"),
            "range_to": chunk_end.strftime("%Y-%m-%d"),
            "cont_flag": "1"
        }

        # 🔁 Retry logic
        for attempt in range(3):
            try:
                history = fyers.history(payload)

                if history.get("candles"):

                    df = pd.DataFrame(
                        history["candles"],
                        columns=["timestamp","open","high","low","close","volume"]
                    )

                    df = convert_time(df)
                    df = format_dataframe(df, symbol)

                    all_chunks.append(df)

                    print(f"[{symbol}] OK:", len(df), "rows")

                    first_valid_found = True
                    empty_count = 0

                else:
                    empty_count += 1

                    if rotation % 5 == 0:
                        print(f"[{symbol}] WARNING: No candles")

                break

            except Exception as e:
                print(f"[{symbol}] ERROR:", e, "Retry:", attempt)
                time.sleep(1)

        # 🔥 Stop early if no data in old years
        if not first_valid_found and empty_count > 5:
            print(f"[{symbol}] Skipping old years (no data)")
            break

        rotation += 1

        # ✅ FIX 3: Reduced sleep
        time.sleep(0.05)

    if not all_chunks:
        print(f"[{symbol}] No new data")
        return

    main_df = pd.concat(all_chunks, ignore_index=True)

    # Merge old data
    existing_obj = OneMinDataFile.objects.filter(
        symbol=symbol,
        is_deleted=False
    ).first()

    if existing_obj:
        old_df = pd.read_csv(io.BytesIO(existing_obj.file_data))
        main_df = pd.concat([old_df, main_df], ignore_index=True)

    main_df = main_df.drop_duplicates(
        subset=["DATE","TIME","SYMBOL"]
    ).reset_index(drop=True)

    # Save CSV
    file_symbol = symbol.replace(":","_").replace("-","_")
    file_name = f"{file_symbol}_1MIN.csv"

    output = io.BytesIO()
    main_df.to_csv(output, index=False)
    output.seek(0)

    OneMinDataFile.objects.update_or_create(
        symbol=symbol,
        defaults={
            "file_name": file_name,
            "file_data": output.getvalue(),
            "is_deleted": False
        }
    )

    print(f"[{symbol}] Saved to DB:", file_name)

    symbol_end = time.time()
    print(f"[{symbol}] ⏱ Time:", round(symbol_end - symbol_start, 2), "sec")


# =========================================================
# MAIN FUNCTION (PARALLEL)
# =========================================================

def download_1min_data(client_id):

    print("\n==============================")
    print("STARTING 1 MIN DATA DOWNLOAD")
    print("==============================")

    df_symbols = download_bse_symbols()
    symbols = get_filtered_symbols(df_symbols)

    print("Total symbols:", len(symbols))

    today = datetime.now().date()

    if datetime.now().hour < 16:
        end_date = today - timedelta(days=1)
    else:
        end_date = today

    # ✅ FIX 2: Safe worker count
    max_workers = 3

    with ThreadPoolExecutor(max_workers=max_workers) as executor:

        futures = [
            executor.submit(process_symbol, symbol, client_id, end_date)
            for symbol in symbols
        ]

        for future in as_completed(futures):
            future.result()

    print("\n====================================")
    print("DOWNLOAD COMPLETED")
    print("====================================")