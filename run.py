from app import create_app, db
import threading
from app.telegram_bot import main as run_bot

app = create_app()


if __name__ == '__main__':
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()

    print()
    app.run(debug=True,use_reloader=False)