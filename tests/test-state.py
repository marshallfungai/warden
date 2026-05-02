"""
Test the deployment state
"""

from warden.core.state import DeploymentState, DeploymentSnapshot
from warden.nginx.controller import APP_STATE


def test_deployment_state():
    state = DeploymentState()
    assert state.redis_client is not None
    assert state.redis_client.ping()

    # Seed via single write path: set_snapshot
    state.set_snapshot(DeploymentSnapshot.minimal("blue", "green"))
    assert state.get_active() == "blue"
    assert state.get_active_snapshot() is not None
    assert state.get_active_snapshot().active == "blue"

    state.set_snapshot(DeploymentSnapshot.minimal("green", "blue"))
    assert state.get_active() == "green"

    state.set_snapshot(DeploymentSnapshot.minimal("blue", "green"))
    assert state.get_active() == "blue"
