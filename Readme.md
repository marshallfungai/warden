
# Warden: Lightweight Deployment Orchestrator  
*A modular, container-native system for zero-downtime deployments — built for resilience, simplicity, and remote 
operation.

## Overview
Lightweight Python orchestrator for container deployment workflows, focused on health-aware rollout logic, Docker integration, and deployment state tracking.

## Project Goal

Warden is an engineering sandbox for building practical orchestration patterns:

- Docker container lifecycle management
- Registry authentication and image pull flows
- Health check + retry behavior
- Redis-backed deployment state
- Nginx config primitives for traffic switching

The project is designed to stay simple, inspectable, and portable.

## Current Status

Warden is under active development. Core modules exist and are being hardened through iterative refactoring and tests.

- Architecture: modular packages under `warden/`
- Runtime target: local Docker/Docker Compose
- Tests: basic tests present in `tests/`
- Focus right now: watcher reliability, deployment correctness, and runtime observability

## Repository Layout

Planned project layout (work in progress; some files are being added):

```text
warden/
├── warden/
│   ├── __init__.py
│   ├── cli.py
│   ├── core/
│   │   ├── orchestrator.py
│   │   ├── state.py
│   │   └── errors.py
│   ├── docker/
│   │   ├── client.py
│   │   ├── registry.py
│   │   └── container.py
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
└── Readme.md
```

## Core Components

- `warden/docker/client.py`: low-level Docker operations (create/get/start/stop/remove/logs/network)
- `warden/docker/container.py`: container instance lifecycle orchestration
- `warden/docker/registry.py`: registry login and pull behavior
- `warden/watcher/registry_watcher.py`: registry polling loop for digest change detection
- `warden/watcher/webhook_server.py`: webhook entrypoint for deploy/rollback triggers
- `warden/health/checker.py`: HTTP health checks with retry/delay logic
- `warden/health/endpoints.py`: framework-specific health endpoint helpers
- `warden/core/state.py`: Redis-backed deployment snapshots (see below)
- `warden/core/errors.py`: typed deployment failures (`DeploymentError` and subclasses)
- `warden/utils/logging.py`: centralized root logger setup (JSON or plain formatter)

### Deployment state (snapshots)

Warden treats **`DeploymentSnapshot`** as the single source of truth for what is deployed. All writes go through **`DeploymentState.set_snapshot(snapshot)`** — there is no separate “set active color only” API, so Redis keys stay consistent.

- **`DeploymentSnapshot`** fields include active/idle slots (`blue` / `green`), version, timestamp, image digest, and container metadata.
- **`DeploymentSnapshot.minimal(active, idle)`** builds a snapshot when only routing slots are known (e.g. rollback with no prior record); optional fields are empty strings / zero as documented in code.
- **Redis keys** (prefix `{app_name}:`):
  - `snapshot:{blue|green}` — JSON for that slot’s last recorded snapshot
  - `active` — active color string (fast pointer)
  - `active_snapshot` — JSON for the currently active deployment (denormalized copy for one-shot reads)

Reads: **`get_active_snapshot()`**, **`get_snapshot(color)`**, **`get_active()`** (color string, derived from snapshot when present).

### Typed deployment errors

Orchestrator steps raise specific exceptions subclassing **`DeploymentError`** (e.g. **`ImagePullError`**, **`ContainerCreateError`**, **`TrafficSwitchError`**) so callers can handle expected failures without catching all `Exception`.

### Logging

Warden configures logging at CLI startup using **`setup_logging()`** in `warden/utils/logging.py`.

- Module loggers use `logging.getLogger(__name__)` for consistent names (`warden.core.orchestrator`, `warden.docker.client`, etc.).
- Root logging can emit either JSON logs (`JSONFormatter`) or plain text.
- A single root handler is configured to avoid duplicate log lines when setup is called multiple times.

### CLI Commands

Current CLI workflow is driven by `warden/cli.py`:

- `warden run` — starts registry watcher loop
- `warden deploy <version>` — runs a targeted deployment
- `warden rollback` — triggers rollback
- `warden status` — prints active snapshot/status
- `warden webhook <port>` — starts webhook server

## Recent changes (changelog)

- **State:** Removed mixed `set_active`; persistence is **`set_snapshot` only**; added **`DeploymentSnapshot.minimal`** for color-only updates.
- **Orchestrator:** Records full snapshots after successful deploy; rollback restores **`get_snapshot(active)`** or falls back to **`minimal`**.
- **Nginx:** **`switch_upstream`** returns success/failure for traffic-switch error handling.

## Tech Stack

- Python 3.x
- Docker SDK for Python (`docker`)
- `requests`
- `redis`
- Docker / Docker Compose

## Local Development

### 1) Clone and enter the project

```bash
git clone <your-repo-url>
cd Warden
```

### 2) Start supporting services

```bash
docker compose up -d
```

### 3) Run tests

```bash
pytest
```

### 4) Run the watcher

```bash
python -m warden.cli run
```

## Roadmap (Near Term)

- Stabilize method contracts across Docker, Registry, and State modules
- Expand tests for health, state, and orchestrator flows
- Add a reproducible end-to-end demo path
- Improve logging and failure diagnostics

## License

`Apache-2.0`
