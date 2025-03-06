🚀 Project Overview
This project integrates Google Login, Google Drive API, and a Real-Time Chatbot using Django.

🔹 Features
✅ Google Authentication – Secure login using Google OAuth2.0
✅ Google Drive Integration – Upload, download, and manage files
✅ Real-Time Chatbot – AI-powered chatbot with live interactions
✅ Django-Based Backend – Secure & scalable API endpoints
✅ WebSocket for Real-Time Chat – Instant messaging with Django Channels

🛠️ Tech Stack
Backend: Django, Django REST Framework
Auth: Google OAuth 2.0
Real-Time Communication: Django Channels, WebSockets
Google Drive API: Google Cloud SDK


📌 Installation & Setup
1️⃣ Clone the Repository
git clone https://github.com/rohansingh9211/Googlefunderbot.git
cd Googlefunderbot
2️⃣ Create a Virtual Environment
python -m venv env
source env/bin/activate  # On Windows use: env\Scripts\activate
3️⃣ Install Dependencies
pip install -r requirements.txt
4️⃣ Set Up Environment Variables
Create a .env file and add the following details:
GOOGLE_CLIENT_ID=<your-google-client-id>
GOOGLE_CLIENT_SECRET=<your-google-client-secret>
GOOGLE_REDIRECT_URI=<your-redirect-uri>
SECRET_KEY=<your-django-secret-key>
5️⃣ Apply Migrations & Start Server
python manage.py migrate
python manage.py runserver

🔑 Google OAuth Setup
Go to Google Developer Console.
Create a new project & enable Google Drive API.
Set up OAuth consent screen and create OAuth Credentials.
Download client_secret.json and place it in the root folder.

💬 WebSocket Chatbot Usage
1. Run Django Channels server
python manage.py runserver
daphne -b 0.0.0.0 -p 8000 enfund.asgi:application
3. Connect to WebSocket: ws://localhost:8000/ws/chat/
4. Start chatting with the AI-powered bot!

📁 Google Drive Integration
Upload a file: POST /api/upload/
Download a file: GET /api/download/{file_id}/
List files: GET /api/drive-files/

👥 Contributors
Rohan Singh - GitHub
