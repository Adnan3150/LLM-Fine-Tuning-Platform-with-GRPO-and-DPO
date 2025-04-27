import os

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 5004))
DEBUG_MODE = os.getenv("DEBUG", "False") == "True"
