from fastapi import FastAPI
import random

app = FastAPI()

# These are the baseline API routes that serve as input for the AST mutation engine.
# The mutator reads this template and generates randomized variants of these endpoints at runtime.
@app.get("/admin/login")
def admin_login():
    return {"status": "Login Page", "auth_token": "X99-KEY", "version": "1.0"}

@app.get("/api/balance")
def get_balance():
    return {"user": "admin", "balance": 4500000, "currency": "USD"}

@app.post("/api/transfer")
def transfer_money(amount: int):
    return {"status": "success", "transferred": amount}

# The root endpoint is intentionally left untouched by mutation—it's used by the dashboard,
# health checks, and boot diagnostics to confirm the system is online.
@app.get("/")
def home():
    return {"message": "Welcome to the Bank. System Operational."}
