import pandas as pd
import io
from accounts.models import BhavcopyFile, GeneratedFile


def create_presence_matrix():

    files = BhavcopyFile.objects.filter(is_deleted=False)

    security_ids = set()

    for f in files:

        df = pd.read_csv(io.BytesIO(f.file_data), usecols=["SECURITY_ID"])

        security_ids.update(df["SECURITY_ID"])

    matrix = pd.DataFrame({"SECURITY_ID": list(security_ids)})

    for f in files:

        date = f.trade_date

        df = pd.read_csv(io.BytesIO(f.file_data), usecols=["SECURITY_ID"])

        matrix[str(date)] = matrix["SECURITY_ID"].isin(df["SECURITY_ID"])

    csv_buffer = io.StringIO()

    matrix.to_csv(csv_buffer, index=False)

    GeneratedFile.objects.create(

        file_name="security_presence_matrix.csv",

        file_data=csv_buffer.getvalue().encode()

    )

    return "Matrix generated"