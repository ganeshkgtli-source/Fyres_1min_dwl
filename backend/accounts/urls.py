from django.urls import path
from .views import (
    register_user,
    login_view,
    fyers_login,
    check_token,
    fyers_callback,
    download_bse_file,
    download_1min_history
)

from . import views

urlpatterns = [

    # AUTH
    path("register/", register_user),
    path("login/", login_view),

    # FYERS
    path("fyers-login/<str:client_id>/", fyers_login),
    path("check-token/<str:client_id>/", check_token),
    path("fyers-callback/", fyers_callback),

    # DOWNLOADS
    path("download-bse/", download_bse_file),
    path("download-1min/", download_1min_history),
    path("download-day/", views.download_day),
    path("download-year/", views.download_year),
    path("download-all/", views.download_all),

    # FILE MANAGEMENT
 path("files/", views.view_files),

path("trash/", views.view_trash),

path("download-selected/", views.download_selected),

path("move-to-trash/", views.delete_selected),

path("delete-permanent/", views.delete_temp),
    # MATRIX
    path("generate-matrix/", views.generate_matrix),
    path("download-matrix/", views.download_matrix),
    path("matrix-file/", views.matrix_file),

    # LOGS
    path("logs/", views.log_dashboard),
]