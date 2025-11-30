# dynamic_server.py
# Loads mutated app from /tmp/active_server.py and exposes 'app' for uvicorn
import importlib.util
import os
import time
import traceback

RUNTIME_OUTPUT_PATH = "/tmp/active_server.py"

def load_active_app(max_retries: int = 8, delay: float = 0.5):
    for i in range(max_retries):
        try:
            if not os.path.exists(RUNTIME_OUTPUT_PATH):
                raise FileNotFoundError(f"{RUNTIME_OUTPUT_PATH} not present")
            spec = importlib.util.spec_from_file_location("active_server", RUNTIME_OUTPUT_PATH)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            if hasattr(module, "app"):
                return module.app
            raise AttributeError("mutated module does not expose 'app'")
        except Exception as e:
            if i == max_retries - 1:
                print(f"[DYNAMIC_SERVER][ERROR] Final failure loading mutated server: {e}")
                print(traceback.format_exc())
                raise
            time.sleep(delay)
    raise RuntimeError("Unable to load mutated app")

# Load at import time so uvicorn dynamic_server:app picks it up
app = load_active_app()
