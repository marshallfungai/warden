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
from pathlib import path

sys.path.insert(0, str(Path(__file__).parent.parent))

from warden.core.orchestrator import DeploymentOrchestrator
from warden.utils.logging import setup_logging

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

    args = parser.parse_args()

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

def deploy_service(version:str):
    """
    Deploy a new version of the service
    """
    from warden.core.orchestrator import Orchestrator
    orchestrator = Orchestrator()
    result = orchestrator.deploy(version)
    if not result:
        sys.exit(1)

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


if __name == "__main__":
    main()