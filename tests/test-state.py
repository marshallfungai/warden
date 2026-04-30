"""
Test the deployment state
"""

import pytest
from warden.core.state import DeploymentState
from warden.nginx.controller import APP_STATE

def test_deployment_state():
    state = DeploymentState()
    assert state.redis_client is not None
    assert state.redis_client.ping()
    assert state.redis_client.get("active") is not None
    assert state.redis_client.get("active") == "blue"
    state.set_active("green")
    assert state.redis_client.get("active") == "green"
    assert state.get_active() == "green"
    state.set_active("blue")
    assert state.redis_client.get("active") == "blue"
    assert state.get_active() == "blue"
    state.set_active(APP_STATE.GREEN)