# core/proxy.py
# This component acts as the traffic director. All requests enter through here,
# where the proxy decides whether to forward the request to the currently active
# mutated backend node or divert it into the honeypot. It also keeps track of
# the latest mutation map and gracefully handles staggered startup conditions.

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
from typing import Dict

# Adjust import path so this proxy can call into the mutation engine
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from mutator import run_mutation  # type: ignore

init(autoreset=True)
app = FastAPI()

# Backend node definitions—these correspond to the two Uvicorn instances
# started in start.sh. Only one node is active at a time.
NODES = [
    {"name": "ALPHA", "url": "http://127.0.0.1:8001"},
    {"name": "BETA",  "url": "http://127.0.0.1:8002"}
]

MUTATION_INTERVAL = 25
current_node_index = 0
current_mapping: Dict[str, str] = {}
ip_reputation: Dict[str, int] = {}
STATE_PATH = "/tmp/mutation_state.json"

# Payload returned to attackers when they probe stale or invalid endpoints.
FAKE_DB = {
    "status": "CRITICAL_SUCCESS",
    "user_data": {
        "username": "admin_root",
        "permissions": "UNLIMITED",
        "account_flag": "TRAP_DOOR_ACTIVATED_IP_LOGGED"
    },
    "system_message": "Root access granted. Downloading database..."
}

def print_log(source: str, message: str, color: Fore = Fore.WHITE):
    # Standardized colored logging for clear visibility during runtime.
    print(f"{color}[{source}] {message}{Style.RESET_ALL}")

def load_state_from_tmp() -> Dict[str, str]:
    # Attempts to restore the most recent route mapping from /tmp.
    # This allows the proxy to survive noisy boot conditions or node restarts.
    try:
        if os.path.exists(STATE_PATH):
            with open(STATE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                return data
    except Exception as e:
        print_log("PROXY", f"Failed reading /tmp state: {e}", Fore.YELLOW)
    return {}

@app.on_event("startup")
async def start_engine():
    # Boot sequence: attempt to load existing state, and fall back to generating
    # one if the system is starting fresh or the previous state was missing.
    global current_mapping
    print_log("SYSTEM", "Booting CHAMELEON Engine...", Fore.CYAN)

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
    # Background loop that periodically triggers new AST mutation cycles and
    # rotates the active backend node so that the attack surface keeps shifting.
    global current_mapping, current_node_index
    while True:
        await asyncio.sleep(MUTATION_INTERVAL)
        try:
            print_log("MUTATOR", "Rewriting AST...", Fore.YELLOW)
            current_mapping = run_mutation()
        except Exception as e:
            print_log("ERROR", f"Mutation failed: {e}", Fore.RED)
            print(traceback.format_exc())

        current_node_index = (current_node_index + 1) % len(NODES)
        active_node = NODES[current_node_index]
        print_log("SWITCH", f"Traffic re-routed to Node {active_node['name']}", Fore.GREEN)

@app.api_route("/{path_name:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def gateway(path_name: str, request: Request):
    # Main proxy routing handler. Decides between forwarding requests or
    # activating deception paths depending on whether the route is still valid.
    global current_mapping, ip_reputation
    original_path = f"/{path_name}"
    target_node = NODES[current_node_index]
    client_ip = request.client.host or "127.0.0.1"

    # Basic resistance mechanism: slow down any IP that has triggered traps before.
    suspicion_score = ip_reputation.get(client_ip, 0)
    if suspicion_score > 0:
        await asyncio.sleep(secrets.randbelow(10) / 10.0)

    # If the proxy lost its in-memory state, try restoring from /tmp at runtime.
    if not current_mapping:
        current_mapping = load_state_from_tmp()

    # If the requested route is valid, forward it to the active node.
    if original_path in current_mapping:
        actual_path = current_mapping[original_path]
        target_url = f"{target_node['url']}{actual_path}"
        print_log("PROXY", f"Forwarding: {original_path} -> {actual_path}", Fore.CYAN)

        transport = httpx.AsyncHTTPTransport(retries=3)
        async with httpx.AsyncClient(transport=transport) as client:
            try:
                req_body = await request.body()
                # Strip or adjust headers that may interfere with upstream behavior.
                headers = {k: v for k, v in request.headers.items() if k.lower() not in ("host", "content-length")}
                resp = await client.request(
                    method=request.method,
                    url=target_url,
                    headers=headers,
                    content=req_body,
                    params=request.query_params,
                    timeout=5.0
                )
                try:
                    content = resp.json()
                except Exception:
                    content = resp.text
                return JSONResponse(content=content, status_code=resp.status_code)
            except Exception as e:
                print_log("PROXY", f"Forwarding error: {e}", Fore.RED)
                return JSONResponse(content={"error": "Node Sync Error"}, status_code=503)

    # Requests for routes that no longer exist (i.e., mutated out) are treated
    # as hostile or replayed attacks and are funneled into the honeypot.
    print_log("SECURITY", f"⚠️ INTRUSION DETECTED: {original_path}", Fore.RED)
    ip_reputation[client_ip] = ip_reputation.get(client_ip, 0) + 1
    await asyncio.sleep(0.3)
    return JSONResponse(content=FAKE_DB, status_code=200)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
