# dynamic_server.py (NEW at project root)
import importlib.util
import os
import time

RUNTIME_OUTPUT_PATH = "/tmp/active_server.py"

def load_active_app():
    if not os.path.exists(RUNTIME_OUTPUT_PATH):
        raise FileNotFoundError(f"Mutated server not found at {RUNTIME_OUTPUT_PATH}")
    spec = importlib.util.spec_from_file_location("active_server", RUNTIME_OUTPUT_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if hasattr(module, "app"):
        return module.app
    raise AttributeError("mutated module does not expose 'app'")

# try to load; uvicorn imports this file once and expects `app` variable
# small retry loop so if start-up ordering causes a race we wait a bit
max_retries = 5
for i in range(max_retries):
    try:
        app = load_active_app()
        break
    except Exception as e:
        if i == max_retries - 1:
            raise
        time.sleep(0.5)
