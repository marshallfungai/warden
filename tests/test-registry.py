"""Unit tests for registry client behavior."""

from types import SimpleNamespace

from warden.docker.registry import RegistryClient


class FakeImages:
    def __init__(self):
        self.last_pull = None
        self.last_get = None
        self.next_pull = SimpleNamespace(id="sha256:pull")
        self.next_get = SimpleNamespace(
            id="sha256:imageid",
            attrs={"RepoDigests": ["repo/demo@sha256:digest123"]},
        )

    def pull(self, full_image):
        self.last_pull = full_image
        return self.next_pull

    def get(self, full_image):
        self.last_get = full_image
        return self.next_get


def make_registry(registry_url="example.registry.io"):
    fake_images = FakeImages()
    registry = object.__new__(RegistryClient)
    registry.registry = registry_url
    registry.client = SimpleNamespace(images=fake_images)
    return registry, fake_images


def test_pull_builds_full_image_reference():
    registry, images = make_registry()

    pulled = registry.pull("myteam/demo-app", "latest")

    assert pulled is not None
    assert images.last_pull == "example.registry.io/myteam/demo-app:latest"


def test_get_image_digest_uses_repo_digests_when_available():
    registry, images = make_registry()

    digest = registry.get_image_digest("myteam/demo-app", "v1")

    assert images.last_get == "example.registry.io/myteam/demo-app:v1"
    assert digest == "sha256:digest123"


def test_get_image_digest_falls_back_to_image_id():
    registry, _ = make_registry()
    registry.client.images.next_get = SimpleNamespace(
        id="sha256:imageid-fallback",
        attrs={"RepoDigests": [None]},
    )

    digest = registry.get_image_digest("myteam/demo-app", "v2")

    assert digest == "sha256:imageid-fallback"
