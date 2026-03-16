from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from django.contrib.auth.hashers import check_password
from datetime import date
from urllib.parse import quote
from django.shortcuts import redirect

from fyers_apiv3 import fyersModel

from .utils.fyers_auth import generate_fyers_token
from .models import User, AccessToken
from .serializers import LoginSerializer, RegisterSerializer

import datetime
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
 
from accounts.services.symbol_service import download_bse_symbols, get_filtered_symbols
from accounts.services.downloader.bhavcopy_downloader import download_bhavcopy
from accounts.services.matrix.matrix_generator import create_presence_matrix
from accounts.services.files.file_service import download_selected_files
 
# USER REGISTER
 
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

 
# USER LOGIN
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

    # TOKEN EXISTS → LOGIN SUCCESS
    if token:
        return Response({
            "status": "login_success",
            "client_id": user.client_id
        })

    # TOKEN NOT FOUND → LOGIN TO FYERS
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


 
# FYERS LOGIN (DIRECT)
 
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

    print("Generated Auth URL:", auth_url)

    return redirect(auth_url)


 
# TOKEN CHECK
 
@api_view(["GET"])
def check_token(request, client_id):

    today = date.today()

    token = AccessToken.objects.filter(
        client_id=client_id,
        token_date=today
    ).first()

    print(f"Checking token for client_id: {client_id}, token found: {bool(token)}")

    if token:
        return Response({"token_exists": True})

    return Response({"token_exists": False})


 
# FYERS CALLBACK
 
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

    print("Access token stored successfully")

    # Redirect to frontend home
    return redirect("http://localhost:5173/")




 

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



from accounts.services.history_service import download_1min_data


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



@api_view(["POST"])
def download_date(request):

    date_str = request.data.get("date")

    date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()

    result = download_bhavcopy(date_obj)

    return Response({"status": result})


@api_view(["POST"])
def generate_matrix(request):

    result = create_presence_matrix()

    return Response({"status": result})


@api_view(["POST"])
def download_files(request):

    ids = request.data.get("ids")

    zip_buffer = download_selected_files(ids)

    response = HttpResponse(zip_buffer, content_type="application/zip")

    response["Content-Disposition"] = "attachment; filename=Bhavcopy.zip"

    return response

import datetime
from django.http import StreamingHttpResponse
from accounts.services.downloader.bhavcopy_downloader import download_bhavcopy

DOWNLOAD_STATE = {}


def stream_logs_year(request, year):

    if year not in DOWNLOAD_STATE:
        DOWNLOAD_STATE[year] = {
            "running": False,
            "logs": []
        }

    def generate():

        state = DOWNLOAD_STATE[year]

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

            log = f"Downloading {current}"
            state["logs"].append(log)
            yield f"data: {log}\n\n"

            result = download_bhavcopy(current)

            state["logs"].append(result)
            yield f"data: {result}\n\n"

            current += datetime.timedelta(days=1)

        finish = f"Completed {year}"
        state["logs"].append(finish)
        yield f"data: {finish}\n\n"

        state["running"] = False

    return StreamingHttpResponse(
        generate(),
        content_type="text/event-stream"
    )