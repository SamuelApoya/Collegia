import os
os.environ.setdefault("OAUTHLIB_INSECURE_TRANSPORT", "1")

from app import create_app
from notifications_scheduler import start_scheduler

app = create_app()

start_scheduler(app, test_mode=True) # to be turned to false whne deploying

if __name__ == "__main__":
    app.run(debug=True)