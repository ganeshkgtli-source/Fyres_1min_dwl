import requests
import zipfile
import io
import datetime
import pandas as pd

from accounts.models import BhavcopyFile, DownloadLog, GeneratedFile


session = requests.Session()

session.headers.update({
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.bseindia.com/markets/MarketInfo/BhavCopy.aspx",
})

session.get("https://www.bseindia.com/markets/MarketInfo/BhavCopy.aspx")


DOWNLOAD_STATE = {}


# -------------------------
# URL BUILDER
# -------------------------

def build_bse_url(date_obj):

    change_date = datetime.date(2024, 7, 8)

    if date_obj < change_date:

        date_str = date_obj.strftime("%d%m%y")

        return "ZIP", f"https://www.bseindia.com/download/BhavCopy/Equity/EQ{date_str}_CSV.ZIP"

    else:

        date_str = date_obj.strftime("%Y%m%d")

        return "CSV", f"https://www.bseindia.com/download/BhavCopy/Equity/BhavCopy_BSE_CM_0_0_0_{date_str}_F_0000.CSV"


# -------------------------
# SYMBOL MAP
# -------------------------

symbol_df = pd.read_csv("./BSE_CM_symbol_list1.csv", header=None)

mapping_df = symbol_df.iloc[:, [12, 9]]

symbol_map = dict(zip(mapping_df.iloc[:, 0], mapping_df.iloc[:, 1]))


# -------------------------
# PROCESS OLD FORMAT
# -------------------------

def process_csv_before_2024(file_bytes):

    df = pd.read_csv(io.BytesIO(file_bytes))

    df = df.rename(columns={
        "SC_CODE": "SECURITY_ID",
        "SC_NAME": "SYMBOL",
        "SC_GROUP": "SERIES",
        "SC_TYPE": "TYPE",
    })

    df["SYMBOL"] = df["SECURITY_ID"].map(symbol_map).fillna(df["SYMBOL"])

    df = df[df["SERIES"].str.startswith(("A", "B"), na=False)]

    df["TYPE"] = df["TYPE"].apply(
        lambda x: "EQUITY" if str(x).upper() == "Q" else x
    )

    cols_to_remove = ["PREVCLOSE", "NET_TURNOV", "TDCLOINDI"]

    df = df.drop(columns=[c for c in cols_to_remove if c in df.columns])

    df = df[
        [
            "SECURITY_ID",
            "SYMBOL",
            "SERIES",
            "TYPE",
            "OPEN",
            "HIGH",
            "LOW",
            "CLOSE",
            "NO_TRADES",
            "NO_OF_SHRS"
        ]
    ]

    output = io.StringIO()

    df.to_csv(output, index=False)

    return output.getvalue().encode()


# -------------------------
# PROCESS NEW FORMAT
# -------------------------

def process_bhavcopy_after_2024(file_bytes):

    df = pd.read_csv(io.BytesIO(file_bytes))

    df = df.rename(columns={
        "TradDt": "DATE",
        "FinInstrmId": "SECURITY_ID",
        "TckrSymb": "SYMBOL",
        "SctySrs": "SERIES",
        "OpnPric": "OPEN",
        "HghPric": "HIGH",
        "LwPric": "LOW",
        "ClsPric": "CLOSE",
        "TtlNbOfTxsExctd": "NO_OF_TRADE",
        "TtlTradgVol": "NO_OF_SHRS"
    })

    df["SYMBOL"] = df["SECURITY_ID"].map(symbol_map).fillna(df["SYMBOL"])

    df = df[df["SERIES"].str.startswith(("A", "B"), na=False)]

    df["TYPE"] = "EQUITY"

    cols_to_remove = [
        "BizDt","Sgmt","Src","FinInstrmTp","ISIN",
        "XpryDt","FininstrmActlXpryDt","FinInstrmNm",
        "LastPric","PrvsClsgPric","SttlmPric",
        "OpnIntrst","ChngInOpnIntrst",
        "TtlTrfVal","SsnId","NewBrdLotQty",
        "Rmks","Rsvd1","Rsvd2","Rsvd3","Rsvd4"
    ]

    df = df.drop(columns=[c for c in cols_to_remove if c in df.columns])

    df = df[
        [
            "DATE",
            "SECURITY_ID",
            "SYMBOL",
            "SERIES",
            "TYPE",
            "OPEN",
            "HIGH",
            "LOW",
            "CLOSE",
            "NO_OF_TRADE",
            "NO_OF_SHRS"
        ]
    ]

    output = io.StringIO()

    df.to_csv(output, index=False)

    return output.getvalue().encode()


# -------------------------
# SAVE LOG
# -------------------------

def save_log(file_name, trade_date, week_day, status):

    DownloadLog.objects.update_or_create(
        file_name=file_name,
        defaults={
            "trade_date": trade_date,
            "week_day": week_day,
            "status": status
        }
    )


# -------------------------
# DOWNLOAD SINGLE DAY
# -------------------------

def download_bhavcopy(date_obj):

    day_name = date_obj.strftime("%A")

    if BhavcopyFile.objects.filter(trade_date=date_obj).exists():

        return f"Already exists in DB: {date_obj} ({day_name})"

    file_type, url = build_bse_url(date_obj)

    try:

        response = session.get(url, timeout=(3, 40))

        if response.status_code != 200:

            file_name = f"EQ{date_obj.strftime('%d%m%y')}.CSV"

            save_log(file_name, date_obj, day_name, "Not Available")

            return f"File not available: {date_obj}"

        if file_type == "ZIP":

            with zipfile.ZipFile(io.BytesIO(response.content)) as z:

                for file in z.namelist():

                    raw_bytes = z.read(file)

                    processed = process_csv_before_2024(raw_bytes)

                    BhavcopyFile.objects.create(
                        file_name=file,
                        trade_date=date_obj,
                        year=date_obj.year,
                        month=date_obj.strftime("%b").upper(),
                        file_data=processed
                    )

                    save_log(file, date_obj, day_name, "Downloaded")

        else:

            file_name = f"EQ{date_obj.strftime('%d%m%y')}.CSV"

            processed = process_bhavcopy_after_2024(response.content)

            BhavcopyFile.objects.create(
                file_name=file_name,
                trade_date=date_obj,
                year=date_obj.year,
                month=date_obj.strftime("%b").upper(),
                file_data=processed
            )

            save_log(file_name, date_obj, day_name, "Downloaded")

        return f"Downloaded: {date_obj}"

    except Exception as e:

        file_name = f"EQ{date_obj.strftime('%d%m%y')}.CSV"

        save_log(file_name, date_obj, day_name, "Error")

        return f"Error {date_obj}: {e}"
    


# -------------------------------------------------
# DOWNLOAD YEAR
# -------------------------------------------------

def download_year_data(year):

    start_date = datetime.date(year, 1, 1)

    end_date = datetime.date(year, 12, 31)

    current = start_date

    while current <= end_date:

        result = download_bhavcopy(current)

        print(result)

        current += datetime.timedelta(days=1)

    return f"Completed year {year}"


# -------------------------------------------------
# DOWNLOAD ALL YEARS
# -------------------------------------------------

def download_all_data():

    start_year = 2017

    current_year = datetime.date.today().year

    for year in range(start_year, current_year + 1):

        download_year_data(year)

    return "All years downloaded"