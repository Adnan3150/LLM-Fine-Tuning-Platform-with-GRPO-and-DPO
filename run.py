# === run.py ===
from app.web import create_app
from app.trainer import start_background_training
from config import HOST, PORT, DEBUG_MODE
import threading

app = create_app()
threading.Thread(target=start_background_training, daemon=True).start()

if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=DEBUG_MODE)
