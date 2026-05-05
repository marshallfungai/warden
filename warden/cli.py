#!/usr/bin/env python3

"""
Warden - Zero-downtime Deployment Orchestrator

Usage:
    warden run                      # Start the watcher
    warden deploy <version>         # Deploy a specific version
    warden rollback                 # Rollback to previous version
    warden status                   # Show current status
"""

import argparse
import sys
import os
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from warden.utils.logging import setup_logging

logger = logging.getLogger(__name__)

def main():
    """
    Main function for the CLI
    """

    parser = argparse.ArgumentParser(description="Warden - Zero-downtime Deployment Orchestrator")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    subparsers.add_parser("run", help="Run Warden")
    deploy_parser = subparsers.add_parser("deploy", help="Deploy a new version of the service")
    deploy_parser.add_argument("version", help="The version of the service to deploy")
    rollback_parser = subparsers.add_parser("rollback", help="Rollback to the previous version of the service")
    status_parser = subparsers.add_parser("status", help="Show the current active snapshot of the service")

    webhook_parser = subparsers.add_parser("webhook", help="Start the webhook server")
    webhook_parser.add_argument("port", help="The port to start the webhook server on")

    args = parser.parse_args()
    setup_logging()

    if args.command == "run":
        run_warden()
    elif args.command == "deploy":
        deploy_service(args.version)
    elif args.command == "rollback":
        rollback_service()
    elif args.command == "status":
        show_status()
    elif args.command == "help":
        parser.print_help()
    elif args.command == "webhook":
        start_webhook_server(args.port)
    else:
        parser.print_help()

def run_warden():
    """
    Run Warden
    """
    logger.info("Running Warden")
    from warden.watcher.registry_watcher import RegistryWatcher
    registry_watcher = RegistryWatcher(
        registry_url=os.getenv("REGISTRY_URL"),
        image_name=os.getenv("IMAGE_NAME"),
        image_tag=os.getenv("IMAGE_TAG"),
        interval=1000
    )
    registry_watcher.run()

def deploy_service(version:str="latest"):
    """
    Deploy a new version of the service
    """
    from warden.core.orchestrator import Orchestrator
    from warden.core.coordination import Coordination
    orchestrator = Orchestrator()
    coordination = Coordination()

    # acquire a lock to prevent multiple deployments
    lock_id = coordination.acquire_lock("deploy")
    if not lock_id:
        logger.error("Deployment is already in progress")
        sys.exit(1)
    try:
        result = orchestrator.deploy(version)
        if not result:
            sys.exit(1)
    finally:
        coordination.release_lock("deploy", lock_id)

def rollback_service():
    """
    Rollback to the previous version of the service
    """
    from warden.core.orchestrator import Orchestrator
    orchestrator = Orchestrator()
    result = orchestrator.rollback()
    if not result:
        sys.exit(1)

def show_status():
    """
    Show the current active snapshot of the service
    """
    from warden.core.orchestrator import Orchestrator
    orchestrator = Orchestrator()
    status = orchestrator.get_active_snapshot()
    print(status)

def start_webhook_server(port:int=5000):
    """
    Start the webhook server
    """
    from warden.watcher.webhook_server import WebhookServer
    webhook_server = WebhookServer(
        port=port,
        on_deploy=deploy_service,
        on_rollback=rollback_service
    )
    webhook_server.run()


if __name__ == "__main__":
    main()