"""
Test the deployment state
"""

import pytest
from warden.core.state import DeploymentState

def test_deployment_state():
    state = DeploymentState()
    