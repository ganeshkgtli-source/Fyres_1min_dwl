# FYRES Trading Dashboard

## Overview
This is a full-stack trading dashboard application integrating Fyers API for market data (BSE symbols, 1-min data, bhavcopies, history, matrix). 
- **Backend**: Django REST API (with PostgreSQL/SQLite, JWT auth, file storage services).
- **Frontend**: React + Vite + Router, with pages for Login/Register, User/Admin Dashboard, Logs, Files, Matrix, OneMinData, Trash.

## Prerequisites
- Python 3.10+
- Node.js 18+ 
- PostgreSQL (recommended; or use SQLite for dev)
- Git
- Fyers developer account/API keys (for auth/data download)

## Quick Start (Development)

### 1. Clone & Navigate
```
git clone <repo> FYRES_NEW
cd FYRES_NEW
```

### 2. Backend Setup
```
cd backend

# Create virtual environment
python -m venv venv
venv\\Scripts\\activate  # Windows

# Install dependencies
pip install django==5.2.12 djangorestframework djangorestframework-simplejwt django-cors-headers python-decouple psycopg2-binary

# Create .env file (copy from example if available, else:)
# SECRET_KEY=your-django-secret-key (generate at https://djecrety.ir/)
# DEBUG=True
# ENCRYPTION_KEY=your-32-char-base64-key (generate: import secrets; print(secrets.token_urlsafe(32)))
# DB_NAME=yourdb
# DB_USER=youruser
# DB_PASSWORD=yourpass
# DB_HOST=localhost
# DB_PORT=5432

# For SQLite dev (edit config/settings.py DATABASES to 'ENGINE': 'django.db.backends.sqlite3', 'NAME': BASE_DIR / 'db.sqlite3')

# Database migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run server
python manage.py runserver
```
Backend API: http://localhost:8000/admin/, /api/ endpoints.

Optional data download:
```
python manage.py download_data
```

### 3. Frontend Setup (new terminal)
```
cd frontend

# Install dependencies
npm install

# Run dev server
npm run dev
```
Frontend: http://localhost:5173

### 4. Usage
- Login/Register via frontend.
- Fyers login for API access (requires Fyers app approval).
- Dashboards: User/Admin views for logs, files, matrix, 1-min data, trash.
- Backend handles data services (bhavcopy, history, symbols).

## Production
- Backend: Use gunicorn/nginx, env vars secure, DEBUG=False.
- Frontend: `npm run build`, serve dist/.
- Database: Production Postgres.
- CORS: Update ALLOWED_HOSTS, CORS origins.

## Troubleshooting
- DB errors: Setup Postgres or switch to SQLite.
- Fyers: Check API logs (fyersRequests.log).
- CORS: Enabled all origins for dev.

## File Structure
```
backend/          Django API + services
  accounts/       Models/views/serializers
  config/         Django settings/urls
  data_files/     CSV data (1-min, symbols)
frontend/         React app
  src/pages/      Dashboards, Login, etc.
```

