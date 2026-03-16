import requests
import datetime
import zipfile
import io

from accounts.models import BhavcopyFile
from .url_builder import build_bse_url
from accounts.services.processing.csv_processor import (
    process_csv_before_2024,
    process_bhavcopy_after_2024
)
from accounts.services.logs.log_service import save_log


session = requests.Session()


def download_bhavcopy(date_obj):

    day_name = date_obj.strftime("%A")

    if BhavcopyFile.objects.filter(trade_date=date_obj).exists():

        return "Already exists"

    file_type, url = build_bse_url(date_obj)

    response = session.get(url)

    if response.status_code != 200:

        save_log("NA", date_obj, day_name, "Not Available")

        return "File not available"

    if file_type == "ZIP":

        with zipfile.ZipFile(io.BytesIO(response.content)) as z:

            for file in z.namelist():

                raw = z.read(file)

                processed = process_csv_before_2024(raw)

                BhavcopyFile.objects.create(

                    file_name=file,

                    trade_date=date_obj,

                    year=date_obj.year,

                    month=date_obj.strftime("%b"),

                    file_data=processed

                )

                save_log(file, date_obj, day_name, "Downloaded")

    else:

        processed = process_bhavcopy_after_2024(response.content)

        file_name = f"EQ{date_obj.strftime('%d%m%y')}.CSV"

        BhavcopyFile.objects.create(

            file_name=file_name,

            trade_date=date_obj,

            year=date_obj.year,

            month=date_obj.strftime("%b"),

            file_data=processed

        )

        save_log(file_name, date_obj, day_name, "Downloaded")

    return "Downloaded"