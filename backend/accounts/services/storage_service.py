import os
import gzip
import io

# Base path (project root)
BASE_DIR = os.getcwd()

# Folder to store CSV files
LOCAL_STORAGE_PATH = os.path.join(BASE_DIR, "data_files")

# Create folder if not exists
os.makedirs(LOCAL_STORAGE_PATH, exist_ok=True)


def save_file(symbol, df):

    file_symbol = symbol.replace(":", "_").replace("-", "_")
    file_name = f"{file_symbol}_1MIN.csv"

    # =========================
    # 1. SAVE CSV LOCALLY
    # =========================
    local_file_path = os.path.join(LOCAL_STORAGE_PATH, file_name)
    df.to_csv(local_file_path, index=False)

    # =========================
    # 2. COMPRESS FOR DB
    # =========================
    buffer = io.BytesIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)

    compressed_data = gzip.compress(buffer.getvalue())

    return file_name, local_file_path, compressed_data


def get_file_data(obj):

    # ✅ Try local file first
    if obj.file_path and os.path.exists(obj.file_path):
        with open(obj.file_path, "rb") as f:
            return f.read()

    # fallback to DB
    try:
        return gzip.decompress(obj.file_data)
    except:
        return obj.file_data