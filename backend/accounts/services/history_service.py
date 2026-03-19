import pandas as pd
import time
import io
from datetime import datetime, timedelta

from accounts.services.fyers_client import get_fyers_client
from accounts.services.symbol_service import download_bse_symbols, get_filtered_symbols
from accounts.services.data_formatter import convert_time
from accounts.services.storage_service import save_file, get_file_data

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

        data = get_file_data(obj)
        df = pd.read_csv(io.BytesIO(data))

        if df.empty or "DATE" not in df.columns:
            return None

        df["DATE"] = pd.to_datetime(df["DATE"], errors="coerce")
        last_date = df["DATE"].max()

        if pd.isna(last_date):
            return None

        return last_date.date()

    except Exception as e:
        print(f"[{symbol}] READ ERROR: {e}")
        return None


# =========================================================
# FORMAT DATAFRAME
# =========================================================
def format_dataframe(df, symbol):

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.dropna(subset=["timestamp"])

    df["SYMBOL"]     = symbol
    df["TIME_FRAME"] = "1_MIN"
    df["DATE"]       = df["timestamp"].dt.date
    df["TIME"]       = df["timestamp"].dt.time
    df["DAY"]        = df["timestamp"].dt.day_name().str.upper()

    market_open = 9 * 60 + 15

    def candle(ts):
        minutes = ts.hour * 60 + ts.minute
        diff = minutes - market_open
        return 0 if diff < 0 else diff + 1

    df["CANDLE_COUNT"] = df["timestamp"].apply(candle)
    df["CATEGORY"]     = "XX"

    df = df.rename(columns={
        "open":   "OPEN",
        "high":   "HIGH",
        "low":    "LOW",
        "close":  "CLOSE",
        "volume": "VOLUME"
    })

    df["TOTAL_VOLUME"] = df.groupby("DATE")["VOLUME"].cumsum()
    df["SHARE_CHECK"]  = ""
    df["CLOSE_DIFF"]   = ""
    df["VOLUME_DIFF"]  = ""

    return df


# =========================================================
# APPEND EOD ROWS
# =========================================================
def append_eod_rows(df, symbol):

    if df.empty:
        return df

    print(f"[{symbol}] Processing EOD rows...")
    df["DATE"] = pd.to_datetime(df["DATE"], errors="coerce").dt.date
    df["TIME"] = pd.to_datetime(df["TIME"].astype(str), format="%H:%M:%S", errors="coerce").dt.time

    bse_symbol = symbol.strip()
    eod_time   = datetime.strptime("15:30:59", "%H:%M:%S").time()
    # dates      = sorted(df["DATE"].unique())
    dates = sorted(set(df["DATE"]))


    bhav_qs = BhavcopyFile.objects.filter(
        trade_date__in=dates,
        is_deleted=False
    )

    bhav_map = {}
    for obj in bhav_qs:
        try:
            bhav = pd.read_csv(io.BytesIO(obj.file_data))
            bhav.columns   = bhav.columns.str.strip().str.upper()
            bhav["SYMBOL"] = bhav["SYMBOL"].astype(str).str.strip()
            bhav_map[obj.trade_date] = bhav
        except Exception as e:
            print(f"[{symbol}] BHAV LOAD ERROR: {e}")

    eod_rows = []

    for date in dates:

        date_obj = pd.to_datetime(date).date()
        bhav     = bhav_map.get(date_obj)

        if bhav is None:
            continue

        row = bhav[bhav["SYMBOL"] == bse_symbol]
        if row.empty:
            continue

        r = row.iloc[0]

        try:
            day_df = df[df["DATE"] == date].sort_values("TIME")

            last_close = None
            last_total = None

            if not day_df.empty:
                last_close = float(day_df.iloc[-1]["CLOSE"])
                last_total = float(day_df.iloc[-1]["TOTAL_VOLUME"])

            eod_close  = float(r["CLOSE"])
            eod_volume = float(r["NO_OF_SHRS"])

            close_diff  = None
            volume_diff = None

            if last_close is not None:
                close_diff = round(eod_close - last_close, 4)

            if last_total is not None:
                volume_diff = int(eod_volume - last_total)

            if last_close is not None and eod_close != last_close:
                eod_close = last_close

            if last_total is not None and eod_volume != last_total:
                eod_volume = last_total

            share_check = "YES" if last_total == eod_volume else "NO"

            eod_rows.append({
                "DATE": date,
                "DAY": pd.Timestamp(date_obj).day_name().upper(),
                "TIME_FRAME": "EOD",
                "CATEGORY": "XX",
                "SYMBOL": symbol,
                "CANDLE_COUNT": 999,
                "TIME": eod_time,
                "OPEN": float(r["OPEN"]),
                "HIGH": float(r["HIGH"]),
                "LOW": float(r["LOW"]),
                "CLOSE": eod_close,
                "VOLUME": eod_volume,
                "TOTAL_VOLUME": eod_volume,
                "CLOSE_DIFF": close_diff,
                "VOLUME_DIFF": volume_diff,
                "SHARE_CHECK": share_check
            })

        except Exception as e:
            print(f"[{symbol}] EOD ERROR for {date}: {e}")

    if not eod_rows:
        print(f"[{symbol}] No EOD rows added")
        return df

    print(f"[{symbol}] EOD rows added: {len(eod_rows)}")

    eod_df = pd.DataFrame(eod_rows)
    final_df = pd.concat([df, eod_df], ignore_index=True)

    # SORT FIX
    final_df["TIME_TEMP"] = pd.to_datetime(
        final_df["TIME"].astype(str),
        format="%H:%M:%S",
        errors="coerce"
    )

    final_df = final_df.sort_values(["DATE", "TIME_TEMP"])
    final_df = final_df.drop(columns=["TIME_TEMP"]).reset_index(drop=True)

    return final_df


# =========================================================
# MAIN FUNCTION
# =========================================================
def download_1min_data(client_id):

    print("\n==============================")
    print("STARTING 1 MIN DATA DOWNLOAD")
    print("==============================")

    fyers = get_fyers_client(client_id)

    print("\nFetching symbol list...")

    df_symbols = download_bse_symbols()
    symbols    = get_filtered_symbols(df_symbols)

    print("Total symbols:", len(symbols))

    today = datetime.now().date()
    if datetime.now().hour < 21:
        end_date = today - timedelta(days=1)
    else:
        end_date = today
    

    for i, symbol in enumerate(symbols, 1):

        symbol_start = time.time()

        print(f"\n[{i}/{len(symbols)}]")
        print("===================================")
        print("Downloading:", symbol)
        print("===================================")

        try:

            default_start = datetime(2019, 3, 1).date()
            last_saved    = get_last_saved_date(symbol)

            if last_saved:
                start_date = last_saved + timedelta(days=1)
                print("Resuming from:", start_date)
            else:
                start_date = default_start
                print("Fresh download from:", start_date)

            if start_date > end_date:
                print("Already up-to-date:", symbol)
                continue

            all_chunks = []
            rotation   = 0
            curr       = start_date

            while curr <= end_date:

                chunk_end = min(curr + timedelta(days=99), end_date)

                print(f"ROTATION {rotation} | {curr} -> {chunk_end}")

                payload = {
                    "symbol": symbol,
                    "resolution": "1",
                    "date_format": "1",
                    "range_from": curr.strftime("%Y-%m-%d"),
                    "range_to": chunk_end.strftime("%Y-%m-%d"),
                    "cont_flag": "1"
                }

                try:
                    history = fyers.history(payload)

                    if history.get("candles"):

                        df = pd.DataFrame(
                            history["candles"],
                            columns=["timestamp", "open", "high", "low", "close", "volume"]
                        )

                        df = convert_time(df)
                        df = format_dataframe(df, symbol)

                        all_chunks.append(df)
                        print("OK:", len(df), "rows")

                    else:
                        print("WARNING: No candles")

                except Exception as e:
                    print("ERROR:", e)

                curr = chunk_end + timedelta(days=1)
                rotation += 1
                time.sleep(0.23)

            if not all_chunks:
                print("WARNING: No new data for", symbol)
                continue

            main_df = pd.concat(all_chunks, ignore_index=True)

            existing_obj = OneMinDataFile.objects.filter(
                symbol=symbol,
                is_deleted=False
            ).first()

            if existing_obj:
                print("Merging old data...")
                old_data = get_file_data(existing_obj)
                old_df   = pd.read_csv(io.BytesIO(old_data))
                main_df  = pd.concat([old_df, main_df], ignore_index=True)
            main_df["DATE"] = pd.to_datetime(main_df["DATE"], errors="coerce").dt.date
            main_df["TIME"] = pd.to_datetime(
                 main_df["TIME"].astype(str),
                 format="%H:%M:%S",
                errors="coerce"
                ).dt.time

            main_df = main_df.drop_duplicates(
                subset=["DATE", "TIME", "SYMBOL"]
            ).reset_index(drop=True)

            print("Appending EOD rows...")
            main_df = main_df[main_df["TIME_FRAME"] != "EOD"].copy()
            main_df = append_eod_rows(main_df, symbol)
            main_df["DATE"] = main_df["DATE"].astype(str)
            main_df["TIME"] = main_df["TIME"].astype(str)

            # ✅ FINAL COLUMN ORDER (MATCHES YOUR SCREENSHOT)
            FINAL_COLUMNS = [
                "DATE", "DAY", "TIME_FRAME", "CATEGORY", "SYMBOL",
                "CANDLE_COUNT", "TIME",
                "OPEN", "HIGH", "LOW", "CLOSE",
                "VOLUME", "TOTAL_VOLUME",
                "SHARE_CHECK", "CLOSE_DIFF", "VOLUME_DIFF"
            ]

            for col in FINAL_COLUMNS:
                if col not in main_df.columns:
                    main_df[col] = ""

            main_df = main_df[FINAL_COLUMNS]

            file_name, file_path, compressed_data = save_file(symbol, main_df)

            OneMinDataFile.objects.update_or_create(
                symbol=symbol,
                defaults={
                    "file_name": file_name,
                    "file_path": file_path,
                    "file_data": compressed_data,
                    "is_deleted": False
                }
            )

            symbol_end = time.time()
            print("Saved to DB:", file_name)
            print(f"⏱ Time for {symbol}: {symbol_end - symbol_start:.2f} sec")

        except Exception as e:
            print(f"[{symbol}] FATAL ERROR: {e}")

    print("\n====================================")
    print("DOWNLOAD COMPLETED")
    print("====================================")