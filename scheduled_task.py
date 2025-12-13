import os
os.environ.setdefault("OAUTHLIB_INSECURE_TRANSPORT", "1")

from app import create_app
from notifications_scheduler import check_upcoming_meetings

app = create_app()

if __name__ == "__main__":
    print("Running scheduled task...")
    check_upcoming_meetings(app)
    print("Task completed!")