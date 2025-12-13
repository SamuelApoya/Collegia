import os

# Allow OAuth over HTTP locally only
if not os.getenv("DYNO"):
    os.environ.setdefault("OAUTHLIB_INSECURE_TRANSPORT", "1")

from app import create_app
from notifications_scheduler import start_scheduler

app = create_app()

# Scheduler runs ONLY locally
if not os.getenv("DYNO"):
    start_scheduler(app)

if __name__ == "__main__":
    app.run(debug=True)
