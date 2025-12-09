import os
os.environ.setdefault("OAUTHLIB_INSECURE_TRANSPORT", "1")

from app import create_app
from notifications_scheduler import start_scheduler

app = create_app()

# Start the notification scheduler
start_scheduler(app)

if __name__ == "__main__":
    app.run(debug=True)