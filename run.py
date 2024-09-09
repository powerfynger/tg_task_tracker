import threading
import schedule
import time 
from datetime import datetime, timedelta

from app import create_app, db
from app.telegram_bot import main as run_bot
from app.models import reset_planned_for_tomorrow, reset_productivity_time

app = create_app()

def schedule_daily_clear():
    while True:
        now = datetime.now()
        midnight = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        time.sleep((midnight - now).total_seconds())
        with app.app_context():
            reset_planned_for_tomorrow() 
            reset_productivity_time()

def run_backend_app():
    app.run(debug=True,use_reloader=False)

if __name__ == '__main__':
    schedule.every().day.at("00:00").do(reset_planned_for_tomorrow)

    schedule_thread = threading.Thread(target=schedule_daily_clear)
    backend_thread = threading.Thread(target=run_backend_app)

    schedule_thread.daemon = True
    backend_thread.daemon = True

    schedule_thread.start()
    backend_thread.start()

    run_bot()

