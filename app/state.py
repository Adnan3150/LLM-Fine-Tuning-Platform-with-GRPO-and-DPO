import threading
import os
# Store session info by session_id
session_store = {}
prompt_queue = []
state_lock = threading.Lock()
MODEL_PATH = os.getenv("MODEL_PATH", "/model/deepseek_model")
LORA_PATH = os.getenv("LORA_PATH", "lora_adapters")
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 5150))
DEBUG_MODE = os.getenv("DEBUG", "False") == "True"