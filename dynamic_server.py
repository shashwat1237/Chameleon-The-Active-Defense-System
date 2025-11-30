# dynamic_server.py
# This loader is responsible for pulling in the most recently mutated FastAPI
# application from /tmp/active_server.py. Uvicorn imports this file and picks up
# whatever version of the app the mutation engine generated at runtime.

import importlib.util
import os
import time
import traceback

RUNTIME_OUTPUT_PATH = "/tmp/active_server.py"

def load_active_app(max_retries: int = 8, delay: float = 0.5):
    # Continuously attempts to import the latest mutated server. This is needed
    # because the mutator may not have produced the file yet when the system starts.
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
            # Only raise the error after exhausting all retry attempts.
            if i == max_retries - 1:
                print(f"[DYNAMIC_SERVER][ERROR] Final failure loading mutated server: {e}")
                print(traceback.format_exc())
                raise
            time.sleep(delay)

    raise RuntimeError("Unable to load mutated app")

# The app is loaded as soon as this module is imported so that uvicorn
# (via `uvicorn dynamic_server:app`) always receives the current mutated instance.
app = load_active_app()
