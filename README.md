# 🧘 Remote Work Break Reminder

A wellness-focused tool to help remote workers take regular breaks, stay productive, and avoid burnout.

It offers customizable break intervals, email reminders, and a simple dashboard for tracking rest habits - all aimed at promoting a healthier work-from-home lifestyle.

---

## ✨ Features

- ⏰ **Custom Break Intervals** - Define your own work/rest rhythm  
- 📬 **Email Notifications** - Get break reminders sent to your inbox  
- 📊 **Break Tracking Dashboard** - Visual overview of break history  
- 💬 **Inspirational Quotes** - Encouragement from [ZenQuotes API](https://zenquotes.io)  
- ✅ **CI/CD** - Code style check & tests via GitHub Actions  
- 🐋 **Dockerized** - Easy to run with Docker and Docker Compose  

---

## 🛠️ Tech Stack

- **Backend:** Django, Django REST Framework  
- **Task Queue:** Celery with Redis as the broker    
- **Testing:** Django test client, pytest  
- **CI/CD:** GitHub Actions  
- **Containerization:** Docker + Docker Compose  

---

## 🚀 Project Structure
- `breaks/` - Main app with models, views, serializers, tasks, and admin
- `config/` - Django settings and Celery configuration
- `tests/` - Unit tests for models, tasks, and views
- `create_superuser.py` - Script to auto-create admin from environment variables
- `docker-entrypoint.sh` - Startup script: waits for Redis, runs migrations, creates superuser
- `Dockerfile` - Builds the Django app image
- `docker-compose.yml` - Defines services: web, Redis, Celery, Celery Beat
- `requirements.txt` - Python dependencies
- `.env` - Environment variables (not committed)
- `.github/workflows/` - GitHub Actions CI (style checks, tests)
- `README.md` - Project documentation

---

## 📦 Setup & Run (Docker)

### 1. Clone the repo:
```bash
git clone https://github.com/yamarko/remote-break-reminder.git
cd remote-break-reminder
```
### 2. Add a `.env` file:
```ini
# Redis settings
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0

# Django superuser (used by create_superuser.py)
DJANGO_SUPERUSER_USERNAME=your_username
DJANGO_SUPERUSER_EMAIL=your_email@example.com
DJANGO_SUPERUSER_PASSWORD=your_password

# Email settings for notifications
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@example.com
EMAIL_HOST_PASSWORD=your_password

# API for inspirational quotes
ZEN_QUOTES_URL=https://zenquotes.io/api/quotes/inspirational
```

### 3. Start the app:
```bash
docker-compose up --build
```
### 4. Access the app:
- Admin: [http://localhost:8000/admin/](http://localhost:8000/admin/)
- Dashboard: [http://localhost:8000/dashboard/](http://localhost:8000/dashboard/)
- Register: [http://localhost:8000/register/](http://localhost:8000/register/)
- Login: [http://localhost:8000/login/](http://localhost:8000/login/)
- Logout: [http://localhost:8000/logout/](http://localhost:8000/logout/)
- API Base URL: [http://localhost:8000/api/](http://localhost:8000/api/)

---

> 💡 If you have problems reaching the ZenQuotes API in Docker (e.g. "Network is unreachable"), try adding Google's DNS servers (`8.8.8.8`, `8.8.4.4`) to your Docker settings.

---

## 📡 API Endpoints
Break intervals:
- `GET /api/break-intervals/` - List all break intervals 
- `POST /api/break-intervals/` - Create a new break interval
- `GET /api/break-intervals/{id}/` - Retrieve a specific break interval
- `PUT /api/break-intervals/{id}/` - Update a break interval
- `PATCH /api/break-intervals/{id}/` - Partial update
- `DELETE /api/break-intervals/{id}/` - Delete a break interval

Break logs:
- `GET /api/break-logs/` - List all break logs (read-only)
- `GET /api/break-logs/{id}/` - Retrieve a specific break log

---

## 🧪 Running Tests

```bash
docker-compose exec web pytest -v
```