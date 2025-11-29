from fastapi import FastAPI
import random

app = FastAPI()

# These endpoints represent the core surfaces the mutation engine rewrites.
# They act as the baseline routes before being transformed at runtime.
@app.get("/admin/login")
def admin_login():
    return {"status": "Login Page", "auth_token": "X99-KEY", "version": "1.0"}

@app.get("/api/balance")
def get_balance():
    return {"user": "admin", "balance": 4500000, "currency": "USD"}

@app.post("/api/transfer")
def transfer_money(amount: int):
    return {"status": "success", "transferred": amount}

# This root route stays stable so health checks and service probes remain predictable.
@app.get("/")
def home():
    return {"message": "Welcome to the Bank. System Operational."}
