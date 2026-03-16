import pandas as pd


def download_bse_symbols():

    print("Downloading BSE Symbol list from FYERS...")

    url = "https://public.fyers.in/sym_details/BSE_CM.csv"

    df = pd.read_csv(url)

    print(f"Total symbols in CSV: {len(df)}")

    return df


def get_filtered_symbols(df):

    # column 9 contains the FYERS symbol
    symbol_col = df.iloc[:, 9].astype(str)

    filtered = symbol_col[
        symbol_col.str.endswith(("-A", "-B"))
    ]

    print(f"Symbols with -A or -B series: {len(filtered)}")

    return filtered.tolist()