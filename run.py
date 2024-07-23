import threading
import schedule
import time 
from datetime import datetime, timedelta

from app import create_app, db
from app.telegram_bot import main as run_bot
from app.models import reset_planned_for_tomorrow

app = create_app()

def schedule_daily_clear():
    while True:
        now = datetime.now()
        midnight = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        time.sleep((midnight - now).total_seconds())
        with app.app_context():
            reset_planned_for_tomorrow() 
    

if __name__ == '__main__':
    schedule.every().day.at("00:00").do(reset_planned_for_tomorrow)

    bot_thread = threading.Thread(target=run_bot)
    schedule_thread = threading.Thread(target=schedule_daily_clear)

    schedule_thread.daemon = True
    bot_thread.daemon = True

    bot_thread.start()
    schedule_thread.start()

    app.run(debug=True,use_reloader=False)