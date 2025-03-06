import json
import os
from django.conf import settings
from django.shortcuts import redirect
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import Flow
from rest_framework.response import Response
from rest_framework.decorators import api_view
import requests
from enfund_view.models import User, googledrive
from dotenv import load_dotenv
from django.shortcuts import render


load_dotenv()

client_config = {
    "web": {
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "project_id": os.getenv("GOOGLE_PROJECT_ID"),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
        "redirect_uris": [os.getenv("GOOGLE_REDIRECT_URI")]
    }
}

@api_view(['GET'])
def google_login(request):
    flow = Flow.from_client_secrets_file(
        client_config,
        scopes=[
            "https://www.googleapis.com/auth/drive.file",
            "https://www.googleapis.com/auth/drive",
            "https://www.googleapis.com/auth/userinfo.profile",
            "openid",
            "https://www.googleapis.com/auth/userinfo.email"
        ],
        # redirect_uri=os.getenv("GOOGLE_REDIRECT_URI")
    )
    auth_url, _ = flow.authorization_url(prompt='consent')
    return Response({'auth_url': auth_url})


@api_view(['GET'])
def google_callback(request):
    code = request.GET.get('code')
    
    flow = Flow.from_client_secrets_file(
        client_config,
        scopes=[
            "https://www.googleapis.com/auth/drive.file",
            "https://www.googleapis.com/auth/drive",
            "https://www.googleapis.com/auth/userinfo.profile",
            "openid",
            "https://www.googleapis.com/auth/userinfo.email"
        ],
        # redirect_uri=os.getenv("GOOGLE_REDIRECT_URI")
    )
    
    flow.fetch_token(code=code)
    credentials = flow.credentials

    user_info_url = os.getenv('GOOGLE_USERINFO')
    headers = {"Authorization": f"Bearer {credentials.token}"}
    response = requests.get(user_info_url, headers=headers)

    if response.status_code == 200:
        user_data = response.json() 
    else:
        user_data = {"error": "Failed to fetch user info"}
        
    if User.objects.filter(email=user_data['email']).exists():
        pass
    else:
        User.objects.create(
            email=user_data['email'],
            social_id=user_data['id'],
            name=user_data['name'],
            account_image=user_data['picture']
        )

    return Response({
        "msg": "User login successfully",
        "access_token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_expiry": credentials.expiry.isoformat() if credentials.expiry else None,
        "id_token": credentials.id_token,
        "scopes": credentials.scopes
    })
    

# @api_view(['POST'])
# def google_drive_upload(request):
#     token = request.data.get("access_token")
#     uploaded_file = request.FILES.get('file')

#     if not uploaded_file:
#         return Response({"error": "No file provided"}, status=400)

#     temp_file_path = f"/tmp/{uploaded_file.name}"
#     with open(temp_file_path, 'wb+') as destination:
#         for chunk in uploaded_file.chunks():
#             destination.write(chunk)

#     try:
#         creds = Credentials(
#             token=os.getenv("GOOGLE_ACCESS_TOKEN"),
#             refresh_token=os.getenv("GOOGLW_REFRESH_TOKEN"),
#             token_uri=os.getenv("GOGGLE_TOKEN_GENERATOR"),
#             client_id=os.getenv("GOOGLE_CLIENT_ID"),
#             client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
#             scopes = ["https://www.googleapis.com/auth/drive.file"]
#         )

#         drive_service = build('drive', 'v3', credentials=creds)
        
#         file_metadata = {'name': uploaded_file.name}
#         media = MediaFileUpload(temp_file_path, mimetype=uploaded_file.content_type)

#         file = drive_service.files().create(body=file_metadata, media_body=media, fields="id").execute()

#         return Response({'file_id': file.get('id')})
#     finally:
#         if os.path.exists(temp_file_path):
#             os.remove(temp_file_path)


@api_view(['POST'])
def google_drive_upload(request):
    access_token = request.headers.get("Authorization")
    if not access_token:
        return Response({"error": "Not authenticated. Please log in."}, status=401)

    file = request.FILES.get("file")
    if not file:
        return Response({"error": "No file provided"}, status=400)

    headers = {"Authorization": f"Bearer {access_token}"}
    metadata = {
        "name": file.name,
        "parents": ["root"]
    }

    files = {
        "data": ("metadata", json.dumps(metadata), "application/json"),
        "file": (file.name, file, file.content_type),
    }

    drive_upload_url = "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart"
    response = requests.post(drive_upload_url, headers=headers, files=files)
    
    user_info_url = os.getenv('GOOGLE_USERINFO')
    headers = {"Authorization": f"Bearer {access_token}"}
    user_res = requests.get(user_info_url, headers=headers)

    user_res = user_res.json()
    if response.status_code == 401:
        return Response({"error": "Unauthorized. Access token may be expired.", "details": response.text}, status=401)

    if response.status_code == 200:
        drive_res = response.json()
        user = User.objects.get(email=user_res.get("email"))
        googledrive.objects.create(
            user=user,
            drive_id=drive_res.get('id')
        )
        return Response({"message": "File uploaded successfully", "file_info": drive_res})
    
    return Response({"error": "File upload failed", "details": response.text}, status=400)



@api_view(['GET'])
def list_drive_files(request):
    
    access_token = request.headers.get("Authorization")
    
    if not access_token:
        if request.headers.get('Accept') == 'application/json':
            return Response({"error": "Not authenticated. Please log in."}, status=401)
        else:
            print("hello")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    params = {
        "fields": "files(id, name, mimeType, size, webViewLink)",
        "q": "trashed=false",  
        "pageSize": 100
    }
    
    drive_files_url = "https://www.googleapis.com/drive/v3/files"
    response = requests.get(drive_files_url, headers=headers, params=params)
    
    if response.status_code == 200:
        if request.headers.get('Accept') == 'application/json':
            return Response(response.json())
        else:
            files = response.json().get('files', [])
            return Response({"file": files})
    else:
        return Response({"error": "Failed to fetch files", "details": response.text}, status=400)
    

@api_view(['GET'])
def drive_download_file(request, file_id):
    access_token = request.headers.get("Authorization")
    
    if not access_token:
        return Response({"error": "Not authenticated. Please log in."}, status=401)
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    file_metadata_url = f"https://www.googleapis.com/drive/v3/files/{file_id}?fields=name,mimeType"
    metadata_response = requests.get(file_metadata_url, headers=headers)
    
    if metadata_response.status_code != 200:
        return Response({"error": "Failed to fetch file metadata", "details": metadata_response.text}, status=400)
    
    file_metadata = metadata_response.json()
    file_name = file_metadata.get("name", "downloaded_file")
    
    download_url = f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media"
    file_response = requests.get(download_url, headers=headers, stream=True)
    
    if file_response.status_code != 200:
        return Response({"error": "Failed to download file", "details": file_response.text}, status=400)
    
    response = Response(
        file_response.content,
        content_type=file_response.headers.get('Content-Type', 'application/octet-stream')
    )
    response['Content-Disposition'] = f'attachment; filename="{file_name}"'
    return response

def chat_view(request):
    return render(request, "chat.html")