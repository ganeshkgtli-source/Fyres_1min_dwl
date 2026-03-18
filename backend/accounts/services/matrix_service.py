import pandas as pd
import io
from datetime import datetime, timedelta

from accounts.models import BhavcopyFile, GeneratedFile


def create_security_presence_matrix():

    print("Starting presence matrix generation...")

    # =========================
    # LOAD UNIQUE SECURITIES
    # =========================
    unique_file = r"C:\FYRES_NEW\backend\unique_security_ids_alldata.csv"

    presence_df = pd.read_csv(unique_file)

    presence_df = presence_df[["SECURITY_ID", "SYMBOL"]]

# Remove duplicates properly
    presence_df = presence_df.drop_duplicates(subset=["SECURITY_ID"])

# Clean values
    presence_df["SECURITY_ID"] = presence_df["SECURITY_ID"].astype(str).str.strip()
    presence_df["SYMBOL"] = presence_df["SYMBOL"].astype(str).str.strip()

    start_date = datetime(2017, 1, 1)
    end_date = datetime.today()

    current_date = start_date

    # =========================
    # LOOP DATES
    # =========================
    while current_date <= end_date:

        year = current_date.strftime("%Y")
        month = current_date.strftime("%b")
        day = current_date.strftime("%d")

        col_name = (year, month, day)

        print("Processing:", current_date.date())

        try:
            bhav_obj = BhavcopyFile.objects.filter(
                trade_date=current_date.date(),
                is_deleted=False
            ).first()

            if not bhav_obj:
                print("Missing in DB:", current_date.date())
                presence_df[col_name] = "NO"
            else:
                df = pd.read_csv(io.BytesIO(bhav_obj.file_data))

                df.columns = df.columns.str.strip().str.upper()

                if "SECURITY_ID" not in df.columns:
                    print("Column missing in:", current_date.date())
                    presence_df[col_name] = "NO"
                else:
                    df = df.drop_duplicates(subset=["SECURITY_ID"])

                    merged = presence_df[["SECURITY_ID", "SYMBOL"]].copy()

                    merged["PRESENT"] = merged["SECURITY_ID"].isin(df["SECURITY_ID"])
                    merged["PRESENT"] = merged["PRESENT"].map({
                        True: "YES",
                        False: "NO"
                    })

                    presence_df[col_name] = merged["PRESENT"]

        except Exception as e:
            print("Error:", current_date.date(), e)
            presence_df[col_name] = "NO"

        current_date += timedelta(days=1)

    # =========================
    # MULTI-LEVEL HEADER
    # =========================
    cols = []
    for col in presence_df.columns:
        if col in ["SECURITY_ID", "SYMBOL"]:
            cols.append((col, ""))
        else:
            cols.append(col)

    presence_df.columns = pd.MultiIndex.from_tuples(cols)

    # =========================
    # SAVE TO DB
    # =========================
    output = io.BytesIO()
    presence_df.to_csv(output, index=False)
    output.seek(0)

    file_name = "security_presence_matrix.csv"

    GeneratedFile.objects.create(
        file_name=file_name,
        file_data=output.getvalue()
    )

    print("Matrix saved to DB")

    return "Matrix generated successfully"

def get_latest_matrix_data():

    obj = GeneratedFile.objects.order_by("-created_at").first()

    if not obj:
        return None

    return obj.file_data   # only return data