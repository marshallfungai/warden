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
