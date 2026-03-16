import pandas as pd
import psycopg2
from django.conf import settings
import io


def create_presence_matrix_from_db():

    conn = psycopg2.connect(
        dbname=settings.DATABASES["default"]["NAME"],
        user=settings.DATABASES["default"]["USER"],
        password=settings.DATABASES["default"]["PASSWORD"],
        host=settings.DATABASES["default"]["HOST"],
        port=settings.DATABASES["default"]["PORT"],
    )

    query = """
        SELECT file_name, file_data
        FROM bhavcopy_files
        WHERE is_deleted = false
    """

    df = pd.read_sql(query, conn)

    if df.empty:
        conn.close()
        return "No bhavcopy data found"

    presence = []

    for _, row in df.iterrows():

        try:
            csv_data = row["file_data"]

            data = pd.read_csv(io.BytesIO(csv_data))

            data["FILE"] = row["file_name"]

            presence.append(data)

        except Exception:
            continue

    if not presence:
        conn.close()
        return "No valid files found"

    combined = pd.concat(presence)

    pivot = combined.pivot_table(
        index="SYMBOL",
        columns="FILE",
        aggfunc="size",
        fill_value=0
    )

    pivot = pivot.applymap(lambda x: 1 if x > 0 else 0)

    csv_buffer = io.StringIO()

    pivot.to_csv(csv_buffer)

    csv_data = csv_buffer.getvalue()

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO generated_files (file_name, file_data)
        VALUES (%s, %s)
        """,
        ("presence_matrix.csv", csv_data)
    )

    conn.commit()
    conn.close()

    return "Matrix generated successfully"


def get_latest_matrix():

    conn = psycopg2.connect(
        dbname=settings.DATABASES["default"]["NAME"],
        user=settings.DATABASES["default"]["USER"],
        password=settings.DATABASES["default"]["PASSWORD"],
        host=settings.DATABASES["default"]["HOST"],
        port=settings.DATABASES["default"]["PORT"],
    )

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT file_name, file_data
        FROM generated_files
        ORDER BY id DESC
        LIMIT 1
        """
    )

    row = cursor.fetchone()

    conn.close()

    return row


def get_latest_matrix_data():

    conn = psycopg2.connect(
        dbname=settings.DATABASES["default"]["NAME"],
        user=settings.DATABASES["default"]["USER"],
        password=settings.DATABASES["default"]["PASSWORD"],
        host=settings.DATABASES["default"]["HOST"],
        port=settings.DATABASES["default"]["PORT"],
    )

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT file_data
        FROM generated_files
        ORDER BY id DESC
        LIMIT 1
        """
    )

    row = cursor.fetchone()

    conn.close()

    return row