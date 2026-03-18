from django.urls import path
from . import views

urlpatterns = [

 
    # AUTH
 
    path("register/", views.register_user),
    path("login/", views.login_view),

 
    # FYERS
 
    path("fyers-login/<str:client_id>/", views.fyers_login),
    path("check-token/<str:client_id>/", views.check_token),
    path("fyers-callback/", views.fyers_callback),

 
    # DOWNLOADS
 
    path("download-bse/", views.download_bse_file),
    path("download-1min/", views.download_1min_history),
      
    # path("stream-download/", views.stream_download_logs),
    path("download-day/", views.download_day),
    path("download-year/", views.download_year),
    path("download-all/", views.download_all),

 
    # FILE MANAGEMENT
 
    path("files/", views.view_files),                  # 🟢 active files
    path("trash/", views.view_trash),                  # 🗑 trash files

    path("download-selected/", views.download_selected),

    path("move-to-trash/", views.move_to_trash),       # move to trash
    path("restore/", views.restore_files),             # restore files
    path("delete-permanent/", views.permanent_delete), # ✅ FIXED (was delete_temp ❌)

 
    # MATRIX
 
    path("generate-matrix/", views.generate_matrix),
    path("download-matrix/", views.download_matrix),
    path("matrix-file/", views.matrix_file),
    # path("view-matrix/", views.view_matrix),

 
    # LOGS
 
    path("logs/", views.log_dashboard),
    
    path("stream-logs/<int:year>/", views.stream_logs),
    path("stream-all-logs/", views.stream_all_logs),
    
    path("1min-files/", views.get_1min_files),


     
]