# core/proxy.py (REPLACE)
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import httpx
import asyncio
import secrets
from colorama import Fore, Style, init
import sys
import os
import json
import traceback

# Ensure core module path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from mutator import run_mutation

init(autoreset=True)
app = FastAPI()

NODES = [
    {"name": "ALPHA", "url": "http://127.0.0.1:8001"},
    {"name": "BETA",  "url": "http://127.0.0.0:8002"}  # keep user's layout; note: ensure ports match start.sh
]
# If you want different ports adjust start.sh accordingly
NODES = [{"name":"ALPHA","url":"http://127.0.0.1:8001"},{"name":"BETA","url":"http://127.0.0.1:8002"}]

MUTATION_INTERVAL = 25
current_node_index = 0
current_mapping = {}
ip_reputation = {}
FAKE_DB = {
    "status": "CRITICAL_SUCCESS",
    "user_data": {
        "username": "admin_root",
        "permissions": "UNLIMITED",
        "account_flag": "TRAP_DOOR_ACTIVATED_IP_LOGGED"
    },
    "system_message": "Root access granted. Downloading database..."
}

def print_log(source, message, color=Fore.WHITE):
    print(f"{color}[{source}] {message}{Style.RESET_ALL}")

# Helper: try to load mapping from /tmp if present
def load_state_from_tmp():
    try:
        p = "/tmp/mutation_state.json"
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                return data
    except Exception as e:
        print_log("PROXY", f"Failed reading /tmp state: {e}", Fore.YELLOW)
    return {}

@app.on_event("startup")
async def start_engine():
    global current_mapping
    print_log("SYSTEM", "Booting CHAMELEON Engine...", Fore.CYAN)

    # Prefer the on-disk /tmp state if present (race-safe)
    current_mapping = load_state_from_tmp()
    if not current_mapping:
        try:
            current_mapping = run_mutation()
            print_log("SYSTEM", "Generated initial mapping via mutator.", Fore.CYAN)
        except Exception as e:
            print_log("ERROR", f"Startup mutator failed: {e}", Fore.RED)
            print(traceback.format_exc())

    asyncio.create_task(mutation_loop())

async def mutation_loop():
    global current_mapping, current_node_index
    while True:
        await asyncio.sleep(MUTATION_INTERVAL)
        try:
            print_log("MUTATOR", "Rewriting AST...", Fore.YELLOW)
            current_mapping = run_mutation()
            # ensure mapping persisted by mutator to /tmp
        except Exception as e:
            print_log("ERROR", f"Mutation failed: {e}", Fore.RED)
            print(traceback.format_exc())

        current_node_index = (current_node_index + 1) % len(NODES)
        active_node = NODES[current_node_index]
        print_log("SWITCH", f"Traffic re-routed to Node {active_node['name']}", Fore.GREEN)

@app.api_route("/{path_name:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def gateway(path_name: str, request: Request):
    global current_mapping, ip_reputation
    original_path = f"/{path_name}"
    target_node = NODES[current_node_index]
    client_ip = request.client.host or "127.0.0.1"

    suspicion_score = ip_reputation.get(client_ip, 0)
    if suspicion_score > 0:
        await asyncio.sleep(secrets.randbelow(10) / 10.0)

    # Refresh mapping from disk occasionally to tolerate external writes
    if not current_mapping:
        current_mapping = load_state_from_tmp()

    if original_path in current_mapping:
        actual_path = current_mapping[original_path]
        target_url = f"{target_node['url']}{actual_path}"
        print_log("PROXY", f"Forwarding: {original_path} -> {actual_path}", Fore.CYAN)
        transport = httpx.AsyncHTTPTransport(retries=3)
        async with httpx.AsyncClient(transport=transport) as client:
            try:
                req_body = await request.body()
                resp = await client.request(
                    method=request.method,
                    url=target_url,
                    headers=request.headers,
                    content=req_body,
                    params=request.query_params,
                    timeout=5.0
                )
                return JSONResponse(content=resp.json(), status_code=resp.status_code)
            except Exception as e:
                print_log("PROXY", f"Forwarding error: {e}", Fore.RED)
                return JSONResponse(content={"error": "Node Sync Error"}, status_code=503)

    print_log("SECURITY", f"⚠️ INTRUSION DETECTED: {original_path}", Fore.RED)
    ip_reputation[client_ip] = ip_reputation.get(client_ip, 0) + 1
    await asyncio.sleep(0.3)
    return JSONResponse(content=FAKE_DB, status_code=200)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
