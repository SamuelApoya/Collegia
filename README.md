# Collegia

A full-stack advising management platform that consolidates fragmented workflows-spreadsheets, manual emails, Google Docs, and multiple calendar apps—into one unified system for students and faculty advisors.

## Overview

Collegia helps students and professors escape the chaos of managing advising sessions across multiple tools by providing:

- One-click booking for students
- Centralized dashboard for professors
- Automated 24-hour and 12-hour email reminders
- Automatic Google Calendar integration
- In-app note-taking and meeting documentation
- Real-time notifications

## Features

### For Students
- Browse available professor time slots
- Book appointments with one click
- Receive automated email reminders
- View upcoming meetings on dashboard
- Track meeting history

### For Professors
- Create and manage availability slots
- View all booked appointments in one place
- Add meeting notes after sessions
- Cancel meetings with automatic student notifications
- Avoid juggling spreadsheets and manual emails

### Automated Features
- 24-hour email reminder before meetings
- 12-hour email reminder on meeting day
- Automatic Google Calendar event creation
- Real-time in-app notifications
- Availability slot management

## Tech Stack

### Backend
- Flask (Python web framework)
- Flask-Login (session management)
- Flask-Dance (Google OAuth)
- Flask-Mail (email notifications)
- Flask-WTF (form handling)
- APScheduler (automated reminders)
- SQLAlchemy (ORM)

### Database
- PostgreSQL (production)
- SQLite (development)

### Frontend
- HTML/CSS/JavaScript
- Responsive design
- WTForms validation

### APIs
- Google OAuth 2.0
- Google Calendar API
- Gmail SMTP

## Installation

### Prerequisites
- Python 3.11+
- PostgreSQL (for production)
- Google Cloud Console account (for OAuth)
- Gmail account (for email notifications)

### Local Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/collegia.git
cd collegia
```

2. Create virtual environment:
```bash
python -m venv venv # OR: python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the root directory:
```
SECRET_KEY=your-secret-key
GOOGLE_OAUTH_CLIENT_ID=your-client-id
GOOGLE_OAUTH_CLIENT_SECRET=your-client-secret
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
DATABASE_URL=sqlite:///collegia.db
```

5. Initialize database:
```bash
python
>>> from app import create_app
>>> from app.extensions import db
>>> app = create_app()
>>> with app.app_context():
...     db.create_all()
>>> exit()
```

6. Run the application:
```bash
python run.py
```

7. Access the application at `http://127.0.0.1:5000`

## Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable Google Calendar API
4. Create OAuth 2.0 credentials
5. Add authorized redirect URIs:
   - `http://localhost:5000/login/google/authorized`
   - `http://localhost:5000/google-callback`
6. Copy Client ID and Client Secret to `.env` file

## Email Setup (Gmail)

1. Enable 2-Factor Authentication on your Gmail account
2. Generate an App Password:
   - Go to Google Account Security
   - Select "App passwords"
   - Generate password for "Mail"
3. Add the 16-character password to `.env` as `MAIL_PASSWORD`

## Deployment (Heroku)

### Prerequisites
- Heroku account
- Heroku CLI installed

### Steps

1. Login to Heroku:
```bash
heroku login
```

2. Create Heroku app:
```bash
heroku create your-app-name
```

3. Add PostgreSQL addon:
```bash
heroku addons:create heroku-postgresql:essential-0
```

4. Add Heroku Scheduler addon:
```bash
heroku addons:create scheduler:standard
```

5. Set environment variables:
```bash
heroku config:set SECRET_KEY=your-secret-key
heroku config:set GOOGLE_OAUTH_CLIENT_ID=your-client-id
heroku config:set GOOGLE_OAUTH_CLIENT_SECRET=your-client-secret
heroku config:set MAIL_SERVER=smtp.gmail.com
heroku config:set MAIL_PORT=587
heroku config:set MAIL_USE_TLS=True
heroku config:set MAIL_USERNAME=your-email@gmail.com
heroku config:set MAIL_PASSWORD=your-app-password
heroku config:set FLASK_ENV=production
```

6. Update Google OAuth redirect URIs:
   - `https://your-app-name.herokuapp.com/login/google/authorized`
   - `https://your-app-name.herokuapp.com/google-callback`

7. Deploy:
```bash
git push heroku main
```

8. Configure Heroku Scheduler:
```bash
heroku addons:open scheduler
```
Add job: `python scheduled_task.py` (run every 10 minutes)

Note: python `scheduled_task.py` is a python script that calls my main snotification scheduling algorithm

9. Open app:
```bash
heroku open
```
