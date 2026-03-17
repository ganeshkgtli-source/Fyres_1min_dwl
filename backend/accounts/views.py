from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.hashers import check_password
from django.shortcuts import redirect
from urllib.parse import quote
from datetime import date
import datetime
import io
import zipfile
from django.http import JsonResponse
from .models import BhavcopyFile
import json
from django.views.decorators.csrf import csrf_exempt
from .models import User, AccessToken, BhavcopyFile, DownloadLog
from .serializers import LoginSerializer, RegisterSerializer

from .utils.fyers_auth import generate_fyers_token

from accounts.services.symbol_service import (
    download_bse_symbols,
    get_filtered_symbols
)

from accounts.services.history_service import download_1min_data

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

    today = date.today()

    token = AccessToken.objects.filter(
        client_id=client_id,
        token_date=today
    ).first()

    if token:
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
        token_date=date.today(),
        defaults={"access_token": access_token}
    )

    return redirect("http://localhost:5173/")


# =========================
# BSE SYMBOL DOWNLOAD
# =========================

def download_bse_file(request):

    try:

        df = download_bse_symbols()

        symbols = get_filtered_symbols(df)

        filtered_df = df[df.iloc[:,9].astype(str).str.endswith(("-A","-B"))]

        filtered_df.to_csv("BSE_CM_symbol_list1.csv", index=False)

        return JsonResponse({
            "status": "success",
            "message": "BSE file downloaded",
            "total_symbols": len(symbols)
        })

    except Exception as e:

        return JsonResponse({
            "status": "error",
            "message": str(e)
        })


# =========================
# 1 MIN DATA DOWNLOAD
# =========================

def download_1min_history(request):

    try:

        client_id = request.GET.get("client_id")

        download_1min_data(client_id)

        return JsonResponse({
            "status":"success",
            "message":"1 minute data downloaded"
        })

    except Exception as e:

        return JsonResponse({
            "status":"error",
            "message":str(e)
        })


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

from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import BhavcopyFile


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