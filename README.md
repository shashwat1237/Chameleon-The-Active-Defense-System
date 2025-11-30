
# 🦎 Chameleon Defense System  
### **Moving Target Defense (MTD) + Active Deception Engine**

<div align="center">

![Status](https://img.shields.io/badge/Status-Active-brightgreen)
![Python](https://img.shields.io/badge/Python-3.9-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED)
![Security](https://img.shields.io/badge/Security-MTD%20Enabled-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

</div>

## 📌 Overview
<img width="1901" height="768" alt="s100" src="https://github.com/user-attachments/assets/242bb6f6-06f5-4552-a185-a8c14fe7bdd2" />


The **Chameleon Defense System** is a next-gen cybersecurity framework built on **Moving Target Defense (MTD)** and **Active Deception**.  
It **mutates API routes every 25 seconds**, deploys a **honeypot for stale routes**, and uses **zero-downtime active/passive node switching** to disrupt automated attacks.

## ❗ Why This Exists — The Problem

Static endpoints create:  
- Infinite attack window  
- Bot-driven mass scanning  
- Weak reactive defenses  

**Static = Vulnerable.**

## 🚀 Core Innovation: AST Mutation Engine  

This system **rewrites FastAPI route decorators using Python AST**, generating new randomized endpoints.

Example:
```
/login → /login_k2r9
/data → /data_x01a
```

## ⭐ Key Features

### 🧬 Dynamic Mutation  
### 🔄 Zero-Downtime Node Switching  
### 🎭 Honeypot for Stale Routes  
### 🐳 Full Dockerized Isolation  

## 🧰 Technology Stack

| Component | Tech |
|----------|------|
| Language | Python 3.9 |
| Backend | FastAPI + Uvicorn |
| Mutation Engine | Python AST |
| Dashboard | Streamlit |
| Proxy Router | HTTPX Async |
| Containerization | Docker |

## 🏗 Architecture

```
                   ┌───────────────────────────────┐
                   │  Reverse Proxy / Route Router  │
                   └───────────────────────────────┘
                                /       \
                  Active Node (Serving)   Passive Node (Mutating)
                             |                    |
                         Real API            AST Mutation
                             |                    |
                         Honeypot Trap (Fake DB)
```

## 📁 Project Structure

```
Chameleon-The-Active-Defense-System/
│
├── core/
│   ├── mutator.py              # AST-based mutation engine (writes mutated server + JSON to /tmp)
│   ├── proxy.py                # Intelligent routing proxy between Node A/B
│   └── __pycache__/            # Auto-generated Python cache
│
├── target_app/
│   ├── template.py             # Base FastAPI template used for each mutation cycle
│   └── __pycache__/            # Auto-generated cache
│
├── demo_scripts/
│   └── hacker_bot.py           # Simulated botnet attacker script (demo for hackathon)
│
├── dashboard.py                 # Streamlit cyber-ops UI (visualizes the entire system)
│
├── start.sh                     # Master runner: runs mutator, nodes, proxy, dashboard
│
├── Dockerfile                   # Containerized deployment config (Render / Docker compatible)
│
├── requirements.txt             # Python dependencies for FastAPI, Streamlit, Proxy, Mutator, etc.
│
├── LICENSE                      # MIT License
│
├── README.md                    # Project documentation
│
└── Chameleon Defense System (Shashwat Shekhar).pdf
|                                 # Project presentation / documentation (hackathon submission)
|
|____dynamic_server.py This loader is responsible for pulling in the most recently mutated FastAPI application from /tmp/active_server.py. Uvicorn imports this file and picks up whatever version of the app the mutation engine generated at runtime.

```

## ⚙ Installation

```bash
git clone https://github.com/shashwat1237/Chameleon-The-Active-Defense-System/tree/main
cd chameleon-defense-system
pip install -r requirements.txt
```

## ▶ Running the System

```bash
bash start.sh
```

## ☁ Deployment

```bash
docker build -t chameleon:v1 .
docker run -p 8000:8000 chameleon:v1
```

## 🧭 Future Roadmap

- Kubernetes auto-scaling  
- AI-driven mutation intervals  
- Automated firewall banlist propagation  

## 📜 License
MIT License.
