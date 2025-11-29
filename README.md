
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

The **Chameleon Defense System** is a next-gen cybersecurity framework built on **Moving Target Defense (MTD)** and **Active Deception**.  
It **mutates API routes every 30 seconds**, deploys a **honeypot for stale routes**, and uses **zero-downtime active/passive node switching** to disrupt automated attacks.

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
/
├── app/
│   ├── main.py
│   ├── mutator/
│   ├── honeypot/
│   └── utils/
├── dashboard/
├── Dockerfile
├── requirements.txt
├── start.sh
└── README.md
```

## ⚙ Installation

```bash
git clone <your-repo-url>
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
