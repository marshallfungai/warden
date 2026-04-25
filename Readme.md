# Warden: Lightweight Deployment Orchestrator  
*A modular, container-native system for zero-downtime deployments — built for resilience, simplicity, and remote operation.*

## Overview
Warden is a self-contained Python toolkit that implements core orchestration patterns (blue/green deployment, health checking, state management) using open-source tools only — no cloud vendor lock-in.

Designed for environments where reliability, auditability, and offline operability matter — such as humanitarian tech, field-deployed systems, or sovereign infrastructure projects.

warden/
├── warden/
│   ├── __init__.py
│   ├── cli.py
│   ├── core/
│   │   ├── orchestrator.py
│   │   ├── state.py
│   │   └── exceptions.py
│   ├── docker/
│   │   ├── client.py
│   │   ├── registry.py
│   │   └── container.py          # Creates containers dynamically
│   ├── health/
│   │   ├── checker.py
│   │   └── endpoints.py
│   ├── nginx/
│   │   ├── controller.py
│   │   └── config.py
│   ├── watcher/
│   │   ├── file_watcher.py
│   │   ├── registry_watcher.py
│   │   └── webhook_server.py
│   └── utils/
│       ├── logging.py
│       └── config.py
├── tests/
│   ├── test_orchestrator.py
│   ├── test_health.py
│   └── test_integration.py
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── setup.py
├── Makefile
└── README.md


## Key Features
- ✅ **Zero-downtime deployments** via blue/green switching  
- ✅ **Health-aware rollout** with retry & timeout logic  
- ✅ **State persistence** using Redis (with graceful fallback)  
- ✅ **Config-driven routing** (nginx integration)  
- ✅ **CLI + Docker-ready** — runs anywhere, including air-gapped setups  
- ✅ **Modular design** — each component (Docker, Health, Nginx, State) is independently testable

## Tech Stack
- Python 3.9+  
- `docker-py`, `redis`, `requests`, `watchdog`, `flask` (optional)  
- No external dependencies beyond standard Linux containers

## Why This Matters for Global Development
UNOPS builds infrastructure to support sustainable development in challenging contexts. Warden reflects the same principles:
> *“Robust, maintainable, and deployable anywhere”* — critical for field operations, low-bandwidth regions, or multi-jurisdictional deployments.

This project demonstrates systems thinking, operational discipline, and infrastructure ownership — skills directly aligned with UNOPS’s mission of delivering vital support to people in need.

---

🔗 [GitHub Repo] • 📄 [Design Doc] • 🧪 `test_phase1.py` → `test_phase8.py` included
