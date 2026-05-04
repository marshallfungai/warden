"""Unit tests for deployment state behavior."""

from warden.core.state import DeploymentSnapshot, DeploymentState


class FakeRedis:
    def __init__(self):
        self.store = {}

    def ping(self):
        return True

    def set(self, key, value):
        self.store[key] = value
        return True

    def get(self, key):
        return self.store.get(key)


def make_state(app_name="demo-app"):
    state = object.__new__(DeploymentState)
    state.app_name = app_name
    state.redis_client = FakeRedis()
    return state


def test_set_snapshot_writes_consistent_keys():
    state = make_state()
    snapshot = DeploymentSnapshot.minimal("blue", "green", version="v1")

    state.set_snapshot(snapshot)

    assert state.redis_client.get("demo-app:active") == "blue"
    assert state.redis_client.get("demo-app:snapshot:blue") is not None
    assert state.redis_client.get("demo-app:active_snapshot") is not None


def test_get_active_snapshot_reads_active_snapshot_payload():
    state = make_state()
    snapshot = DeploymentSnapshot.minimal("green", "blue", version="v2")
    state.set_snapshot(snapshot)

    active_snapshot = state.get_active_snapshot()

    assert active_snapshot is not None
    assert active_snapshot.active == "green"
    assert active_snapshot.idle == "blue"
    assert active_snapshot.version == "v2"


def test_get_active_snapshot_falls_back_to_active_color_lookup():
    state = make_state()
    snapshot = DeploymentSnapshot.minimal("blue", "green", version="v3")
    state.set_snapshot(snapshot)

    # Simulate absence of denormalized key and bytes from Redis.
    state.redis_client.set("demo-app:active_snapshot", None)
    state.redis_client.set("demo-app:active", b"blue")

    active_snapshot = state.get_active_snapshot()
    assert active_snapshot is not None
    assert active_snapshot.active == "blue"
