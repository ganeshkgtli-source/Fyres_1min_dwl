from django.urls import path
from .views import (
    download_1min_history,
    download_bse_file,
    register_user,
    login_view,
    fyers_login,
    check_token,
    fyers_callback
)
from . import views

urlpatterns = [

    path("register/", register_user),
    path("login/", login_view),

    path("fyers-login/<str:client_id>/", fyers_login),
    path("check-token/<str:client_id>/", check_token),
    path("fyers-callback/", fyers_callback),

    path("download-bse/", download_bse_file),

    path("download-1min/", download_1min_history),
        path("download/", views.download_date),

    path("matrix/generate/", views.generate_matrix),

    path("files/download/", views.download_files),
    path("logs/stream/<int:year>/", views.stream_logs_year),
]