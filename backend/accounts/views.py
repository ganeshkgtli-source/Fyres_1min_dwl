from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.hashers import check_password
from django.shortcuts import redirect
from urllib.parse import quote
from datetime import date, timezone
import datetime
import io
import zipfile
from django.http import JsonResponse
from .models import BhavcopyFile
import json
from django.views.decorators.csrf import csrf_exempt
from .models import User, AccessToken, BhavcopyFile, DownloadLog
from .serializers import LoginSerializer, RegisterSerializer
from threading import Thread
import time
from django.http import JsonResponse, StreamingHttpResponse
from .utils.fyers_auth import generate_fyers_token
from threading import Thread
import time
from django.http import JsonResponse, StreamingHttpResponse
from datetime import timedelta
from django.utils import timezone
from accounts.services.symbol_service import (
    download_bse_symbols,
    get_filtered_symbols
)

from accounts.services.history_service import  download_1min_data

from accounts.services.bhavcopy_service import (
    download_bhavcopy,
    download_year_data,
    download_all_data
)

from accounts.services.matrix_service import (
    create_presence_matrix_from_db,
    get_latest_matrix,
    get_latest_matrix_data
)
# views.py

import datetime
from django.http import StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from accounts.models import OneMinDataFile

DOWNLOAD_STATE = {}

# =========================
# USER REGISTER
# =========================

@api_view(["POST"])
def register_user(request):

    serializer = RegisterSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()

        return Response({
            "status": "success",
            "message": "User registered successfully"
        })

    return Response(serializer.errors, status=400)


# =========================
# USER LOGIN
# =========================

@api_view(["POST"])
def login_view(request):

    serializer = LoginSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=400)

    email = serializer.validated_data["email"]
    password = serializer.validated_data["password"]

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({"error": "User not registered"}, status=401)

    if not check_password(password, user.password):
        return Response({"error": "Invalid password"}, status=401)

    today = date.today()

    token = AccessToken.objects.filter(
        client_id=user.client_id,
        token_date=today
    ).first()

    if token:
        return Response({
            "status": "login_success",
            "client_id": user.client_id
        })

    redirect_uri = quote("http://127.0.0.1:8000/api/fyers-callback/")

    auth_url = (
        "https://api-t1.fyers.in/api/v3/generate-authcode"
        f"?client_id={user.client_id}"
        f"&redirect_uri={redirect_uri}"
        "&response_type=code"
        f"&state={user.client_id}"
    )

    return Response({
        "status": "fyers_login",
        "auth_url": auth_url,
        "client_id": user.client_id
    })


# =========================
# FYERS LOGIN
# =========================

@api_view(["GET"])
def fyers_login(request, client_id):

    try:
        user = User.objects.get(client_id=client_id)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=404)

    redirect_uri = quote("http://127.0.0.1:8000/api/fyers-callback/")

    auth_url = (
        "https://api-t1.fyers.in/api/v3/generate-authcode"
        f"?client_id={user.client_id}"
        f"&redirect_uri={redirect_uri}"
        "&response_type=code"
        f"&state={user.client_id}"
    )

    return redirect(auth_url)


# =========================
# TOKEN CHECK
# =========================

@api_view(["GET"])
def check_token(request, client_id):

    token = AccessToken.objects.filter(
        client_id=client_id
    ).order_by("-created_at").first()

    if not token:
        return Response({"token_exists": False})

    # ✅ 24-hour validation
    if timezone.now() <= token.created_at + timedelta(hours=24):
        return Response({"token_exists": True})

    return Response({"token_exists": False})

# =========================
# FYERS CALLBACK
# =========================

def fyers_callback(request):

    auth_code = request.GET.get("auth_code") or request.GET.get("code")
    client_id = request.GET.get("state")

    if not auth_code or not client_id:
        return JsonResponse({"error": "Missing auth_code or state"})

    try:
        user = User.objects.get(client_id=client_id)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"})

    access_token = generate_fyers_token(user, auth_code)

    if not access_token:
        return JsonResponse({"error": "Token generation failed"})

    AccessToken.objects.update_or_create(
    client_id=user.client_id,
    defaults={
        "access_token": access_token,
        "created_at": timezone.now()  # force refresh time
    }
)

    return redirect("http://localhost:5173/")


# =========================
# BSE SYMBOL DOWNLOAD
# =========================
def download_bse_file(request):

    try:
        df = download_bse_symbols()

        # column 9 = fyers symbol
        df["fyers_symbol"] = df.iloc[:, 9].astype(str)

        # filter (-A, -B)
        filtered_df = df[
            df["fyers_symbol"].str.endswith(("-A", "-B"))
        ]

        # ✅ Convert to CSV (in memory)
        csv_buffer = io.StringIO()
        filtered_df.to_csv(csv_buffer, index=False)
        csv_bytes = csv_buffer.getvalue().encode()

        # ✅ Save in DB
        OneMinDataFile.objects.create(
            symbol="BSE_CMLIST",   # 🔥 this is what you wanted
            file_name="BSE_CM_symbol_list.csv",
            file_data=csv_bytes
        )

        return JsonResponse({
            "status": "success",
            "message": "BSE CM list stored in DB",
            "total_symbols": len(filtered_df)
        })

    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": str(e)
        })

# =========================
# 1 MIN DATA DOWNLOAD
# =========================

 


# =============================
# START DOWNLOAD
# =============================
def download_1min_history(request):

    try:
        client_id = request.GET.get("client_id")

        Thread(target=download_1min_data, args=(client_id,)).start()

        return JsonResponse({
            "status": "success",
            "message": "Download started"
        })

    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": str(e)
        })


# =============================
# STREAM LOGS (SSE)
# =============================

def stream_1min_logs(request):

    client_id = request.GET.get("client_id")

    def event_stream():
        for log in download_1min_data(client_id):
            yield f"data: {log}\n\n"

    return StreamingHttpResponse(
        event_stream(),
        content_type="text/event-stream"
    )

# =========================
# BHAVCOPY DOWNLOAD
# =========================

@api_view(["POST"])
def download_day(request):

    date_str = request.data.get("date")

    date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()

    result = download_bhavcopy(date_obj)

    return Response({"message": result})


@api_view(["POST"])
def download_year(request):

    year = request.data.get("year")

    if not year:
        return Response({"error": "Year required"}, status=400)

    result = download_year_data(int(year))

    return Response({"message": result})


@api_view(["POST"])
def download_all(request):

    result = download_all_data()

    return Response({"message": result})


# =========================
# FILE MANAGEMENT
# =========================

@api_view(["POST"])
def download_selected(request):
    ids = request.data.get("ids", [])

    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w") as z:
        files = BhavcopyFile.objects.filter(id__in=ids)

        for f in files:
            z.writestr(
                f"Bhavcopy/{f.year}/{f.month}/{f.file_name}",
                f.file_data
            )

    zip_buffer.seek(0)

    response = HttpResponse(zip_buffer.getvalue(), content_type="application/zip")
    response["Content-Disposition"] = 'attachment; filename="Bhavcopy.zip"'

    return response


@api_view(["POST"])
def move_to_trash(request):
    ids = request.data.get("ids", [])

    files = BhavcopyFile.objects.filter(id__in=ids)

    files.update(is_deleted=True)

    DownloadLog.objects.filter(
        file_name__in=files.values_list("file_name", flat=True)
    ).update(status="deleted")

    return Response({"message": "Moved to trash"})


@api_view(["POST"])
def restore_files(request):
    ids = request.data.get("ids", [])

    files = BhavcopyFile.objects.filter(id__in=ids)

    files.update(is_deleted=False)

    DownloadLog.objects.filter(
        file_name__in=files.values_list("file_name", flat=True)
    ).update(status="active")

    return Response({"message": "Restored"})


@api_view(["POST"])
def permanent_delete(request):
    ids = request.data.get("ids", [])

    files = BhavcopyFile.objects.filter(id__in=ids, is_deleted=True)

    file_names = list(files.values_list("file_name", flat=True))

    DownloadLog.objects.filter(file_name__in=file_names).delete()

    files.delete()

    return Response({"deleted_ids": ids})


# =========================
# VIEW FILES
# =========================




@api_view(["GET"])
def view_files(request):

    year = request.GET.get("year")
    month = request.GET.get("month")

    # BASE QUERY (ONLY ACTIVE FILES)
    files = BhavcopyFile.objects.filter(is_deleted=False)

    # APPLY FILTERS
    if year:
        files = files.filter(year=year)

    if month:
        files = files.filter(month=month)

    # ORDER FILES (LATEST FIRST)
    files = files.order_by("-trade_date")

    # ✅ DISTINCT YEARS (ONLY FROM ACTIVE FILES)
    years = (
        BhavcopyFile.objects
        .filter(is_deleted=False)
        .values_list("year", flat=True)
        .distinct()
        .order_by("year")
    )

    # ✅ DISTINCT MONTHS (ONLY FROM ACTIVE FILES)
    months = (
        BhavcopyFile.objects
        .filter(is_deleted=False)
        .values_list("month", flat=True)
        .distinct()
        .order_by("month")
    )

    return Response({
        "files": [
            {
                "id": f.id,
                "file_name": f.file_name,
                "trade_date": f.trade_date,
                "year": f.year,
                "month": f.month
            }
            for f in files
        ],

        # ✅ CONVERT QUERYSET → LIST
        "years": list(years),
        "months": list(months)
    })

@api_view(["GET"])
def view_trash(request):

    year = request.GET.get("year")
    month = request.GET.get("month")

    files = BhavcopyFile.objects.filter(is_deleted=True)

    # APPLY FILTER
    if year:
        files = files.filter(year=year)

    if month:
        files = files.filter(month=month)

    # ✅ DISTINCT VALUES FOR FILTER DROPDOWN
    years = (
        BhavcopyFile.objects
        .filter(is_deleted=True)
        .values_list("year", flat=True)
        .distinct()
        .order_by("year")
    )

    months = (
        BhavcopyFile.objects
        .filter(is_deleted=True)
        .values_list("month", flat=True)
        .distinct()
        .order_by("month")
    )

    return Response({
        "files": [
            {
                "id": f.id,
                "file_name": f.file_name,
                "trade_date": f.trade_date,
                "year": f.year,
                "month": f.month
            } for f in files
        ],
        "years": list(years),   # ✅ CLEAN LIST
        "months": list(months)  # ✅ CLEAN LIST
    })


# =========================
# MATRIX
# =========================

@api_view(["GET"])
def generate_matrix(request):
    return Response({"status": create_presence_matrix_from_db()})


def download_matrix(request):
    row = get_latest_matrix()

    if not row:
        return HttpResponse("No file")

    name, data = row

    res = HttpResponse(data, content_type="text/csv")
    res["Content-Disposition"] = f'attachment; filename="{name}"'
    return res


def matrix_file(request):
    row = get_latest_matrix_data()
    return HttpResponse(row[0], content_type="text/csv")


# =========================
# LOGS
# =========================

@api_view(["GET"])
def log_dashboard(request):
    logs = DownloadLog.objects.all().order_by("-download_time")

    return Response([
        {
            "file_name": l.file_name,
            "trade_date": l.trade_date,
            "status": l.status,
            "download_time": l.download_time
        }
        for l in logs
    ])


@csrf_exempt
def stream_logs(request, year):

    year = int(year)

    if year not in DOWNLOAD_STATE:
        DOWNLOAD_STATE[year] = {
            "running": False,
            "logs": []
        }

    def generate():
        state = DOWNLOAD_STATE[year]

        # If already running → send old logs
        if state["running"]:
            for log in state["logs"]:
                yield f"data: {log}\n\n"
            return

        state["running"] = True
        state["logs"].clear()

        start_date = datetime.date(year, 1, 1)
        end_date = datetime.date(year, 12, 31)

        current = start_date

        while current <= end_date:

            log = f"Downloading: {current}"
            state["logs"].append(log)
            yield f"data: {log}\n\n"

            result = download_bhavcopy(current)

            state["logs"].append(result)
            yield f"data: {result}\n\n"

            current += datetime.timedelta(days=1)

        finish = f"Completed year {year}"
        state["logs"].append(finish)
        yield f"data: {finish}\n\n"

        state["running"] = False

    return StreamingHttpResponse(
        generate(),
        content_type="text/event-stream"
    )

@csrf_exempt
def stream_all_logs(request):

    key = "all"

    if key not in DOWNLOAD_STATE:
        DOWNLOAD_STATE[key] = {
            "running": False,
            "logs": []
        }

    def generate():
        state = DOWNLOAD_STATE[key]

        if state["running"]:
            for log in state["logs"]:
                yield f"data: {log}\n\n"
            return

        state["running"] = True
        state["logs"].clear()

        start_year = 2017
        current_year = datetime.date.today().year

        for year in range(start_year, current_year + 1):

            log = f"Starting download for {year}"
            state["logs"].append(log)
            yield f"data: {log}\n\n"

            start_date = datetime.date(year, 1, 1)

            if year == current_year:
                end_date = datetime.date.today()
            else:
                end_date = datetime.date(year, 12, 31)

            current = start_date

            while current <= end_date:

                log = f"Downloading: {current}"
                state["logs"].append(log)
                yield f"data: {log}\n\n"

                result = download_bhavcopy(current)

                state["logs"].append(result)
                yield f"data: {result}\n\n"

                current += datetime.timedelta(days=1)

            log = f"Completed year {year}"
            state["logs"].append(log)
            yield f"data: {log}\n\n"

        finish = "Completed all years"
        state["logs"].append(finish)
        yield f"data: {finish}\n\n"

        state["running"] = False

    return StreamingHttpResponse(
        generate(),
        content_type="text/event-stream"
    )

from accounts.models import OneMinDataFile


@api_view(["GET"])
def list_files(request):

    files = OneMinDataFile.objects.filter(is_deleted=False).order_by("-created_at")

    data = []

    for f in files:
        data.append({
            "id": f.id,
            "symbol": f.symbol,
            "file_name": f.file_name,
            "created_at": f.created_at
        })

    return Response(data)




@api_view(["GET"])
def get_1min_files(request):

    symbol = request.GET.get("symbol")

    qs = OneMinDataFile.objects.filter(is_deleted=False)

    if symbol:
        qs = qs.filter(symbol=symbol)

    symbols = qs.values_list("symbol", flat=True).distinct()

    data = [
        {
            "id": f.id,
            "symbol": f.symbol,
            "file_name": f.file_name,
            "created_at": f.created_at.strftime("%d-%m-%Y %H:%M:%S")
        }
        for f in qs
    ]

    return Response({
        "files": data,
        "symbols": list(symbols)
    })

@api_view(["POST"])
def download_1min_selected(request):

    ids = request.data.get("ids", [])

    buffer = io.BytesIO()

    with zipfile.ZipFile(buffer, "w") as z:

        files = OneMinDataFile.objects.filter(id__in=ids)

        for f in files:
            z.writestr(f.file_name, f.file_data)

    buffer.seek(0)

    return HttpResponse(
        buffer,
        content_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=OneMin.zip"}
    )
@api_view(["POST"])
def move_1min_to_trash(request):

    ids = request.data.get("ids", [])

    OneMinDataFile.objects.filter(id__in=ids).update(is_deleted=True)

    return Response({"status":"ok"})

@api_view(["GET"])
def get_trash(request):
    # Fetch deleted OneMinDataFile
    one_min_files = OneMinDataFile.objects.filter(is_deleted=True)
    bhav_files = BhavcopyFile.objects.filter(is_deleted=True)

    # Combine both
    files = []

    for f in one_min_files:
        files.append({
            "id": f"id_om_{f.id}",      # unique ID prefix for frontend
            "file_name": f.file_name,
            "trade_date": f.created_at.strftime("%Y-%m-%d"),
            "year": f.created_at.year,
            "month": f.created_at.strftime("%b").upper(),
            "type": "1MIN"
        })

    for f in bhav_files:
        files.append({
            "id": f"id_bh_{f.id}",      # unique ID prefix for frontend
            "file_name": f.file_name,
            "trade_date": f.trade_date.strftime("%Y-%m-%d"),
            "year": f.year,
            "month": f.month.upper(),
            "type": "BHAVCOPY"
        })

    # Unique years and months
    years = sorted(list({f["year"] for f in files}), reverse=True)
    months = sorted(list({f["month"] for f in files}))

    return Response({
        "files": files,
        "years": years,
        "months": months
    })
@api_view(["POST"])
def restore_trash(request):
    ids = request.data.get("ids", [])

    # Separate IDs by type
    one_min_ids = [int(i.replace("id_om_","")) for i in ids if i.startswith("id_om_")]
    bhav_ids = [int(i.replace("id_bh_","")) for i in ids if i.startswith("id_bh_")]

    OneMinDataFile.objects.filter(id__in=one_min_ids).update(is_deleted=False)
    BhavcopyFile.objects.filter(id__in=bhav_ids).update(is_deleted=False)

    return Response({"status": "restored"})
@api_view(["POST"])
def delete_trash_permanent(request):
    ids = request.data.get("ids", [])

    one_min_ids = [int(i.replace("id_om_","")) for i in ids if i.startswith("id_om_")]
    bhav_ids = [int(i.replace("id_bh_","")) for i in ids if i.startswith("id_bh_")]

    OneMinDataFile.objects.filter(id__in=one_min_ids).delete()
    BhavcopyFile.objects.filter(id__in=bhav_ids).delete()

    return Response({"status": "deleted"})

@api_view(["POST"])
def one_min_move_to_trash(request):
    ids = request.data.get("ids", [])
    if not ids:
        return Response({"error": "No files selected"}, status=400)

    files = OneMinDataFile.objects.filter(id__in=ids)
    updated_count = files.update(is_deleted=True)

    return Response({"success": f"{updated_count} files moved to trash"})