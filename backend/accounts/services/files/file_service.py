import io
import zipfile
from accounts.models import BhavcopyFile


def download_selected_files(ids):

    files = BhavcopyFile.objects.filter(id__in=ids)

    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w") as z:

        for f in files:

            path = f"Bhavcopy/{f.year}/{f.month}/{f.file_name}"

            z.writestr(path, f.file_data)

    zip_buffer.seek(0)

    return zip_buffer