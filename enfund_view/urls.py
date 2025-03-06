from django.urls import path
from .views import chat_view, google_drive_upload, google_login, google_callback, list_drive_files, drive_download_file

urlpatterns = [
    path('api/auth/google-login/', google_login, name='google-login'),
    path('api/auth/callback/', google_callback, name='google-callback'),
    path('api/upload/drive/', google_drive_upload, name='drive-uploader'),
    path('api/get/drive/', list_drive_files, name='drive-fetch'),
    path('api/download/file/<str:file_id>/', drive_download_file, name="download-files"),
    path("chat/", chat_view, name="chat"),
]
