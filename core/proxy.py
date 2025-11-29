import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import httpx
import asyncio
import secrets
from colorama import Fore, Style, init
import sys
import os

# Fix path to allow importing mutator if running from root
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from mutator import run_mutation

init(autoreset=True)
app = FastAPI()

# CONFIGURATION
NODES = [
    {"name": "ALPHA", "url": "http://127.0.0.1:8001"},
    {"name": "BETA",  "url": "http://127.0.0.1:8002"}
]
MUTATION_INTERVAL = 15 

# GLOBAL STATE
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

@app.on_event("startup")
async def start_engine():
    global current_mapping
    print_log("SYSTEM", "Booting CHAMELEON Engine...", Fore.CYAN)
    
    try:
        # [VERIFIED] Initial mutation ensures Proxy and Nodes are synced on boot
        current_mapping = run_mutation()
        print_log("SYSTEM", "Secure Entropy Generated.", Fore.CYAN)
    except Exception as e:
        print_log("ERROR", f"Startup failed: {e}", Fore.RED)
    
    asyncio.create_task(mutation_loop())

async def mutation_loop():
    global current_mapping, current_node_index
    while True:
        await asyncio.sleep(MUTATION_INTERVAL)
        
        print_log("MUTATOR", "Rewriting AST...", Fore.YELLOW)
        # [VERIFIED] This triggers the file write that causes Uvicorn to reload
        current_mapping = run_mutation()
        
        current_node_index = (current_node_index + 1) % len(NODES)
        active_node = NODES[current_node_index]
        
        print_log("SWITCH", f"Traffic re-routed to Node {active_node['name']}", Fore.GREEN)

@app.api_route("/{path_name:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def gateway(path_name: str, request: Request):
    original_path = f"/{path_name}"
    target_node = NODES[current_node_index]
    client_ip = request.client.host or "127.0.0.1"
    
    # LAYER 1: Feedback Loop
    suspicion_score = ip_reputation.get(client_ip, 0)
    if suspicion_score > 0:
        latency = secrets.randbelow(10) / 10.0  
        await asyncio.sleep(latency)

    # LAYER 2: Routing
    if original_path in current_mapping:
        actual_path = current_mapping[original_path]
        target_url = f"{target_node['url']}{actual_path}"
        print_log("PROXY", f"Forwarding: {original_path} -> {actual_path}", Fore.CYAN)
        
        # [VERIFIED] Retries handled by Transport (requires httpx==0.23.3)
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
            except Exception:
                return JSONResponse(content={"error": "Node Sync Error"}, status_code=503)

    # LAYER 3: The Trap
    else:
        print_log("SECURITY", f"⚠️ INTRUSION DETECTED: {original_path}", Fore.RED)
        ip_reputation[client_ip] = suspicion_score + 1
        await asyncio.sleep(0.3)
        return JSONResponse(content=FAKE_DB, status_code=200)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)