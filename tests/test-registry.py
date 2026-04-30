"""
Test the registry client
"""

import pytest
from warden.docker.registry import RegistryClient

def test_registry_client():
    registry = RegistryClient()
    assert registry is not None
    assert registry.login("docker.io") is True
    assert registry.pull("hello-world", "latest") is not None
    assert registry.remove("hello-world", "latest") is True
