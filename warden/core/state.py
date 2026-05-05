"""
State management for Warden
"""

import os
import json
import redis
import logging
from typing import Optional
from dataclasses import dataclass
from dataclasses import asdict

from warden.docker.client import DockerClient
from warden.nginx.controller import APP_STATE

logger = logging.getLogger(__name__)


@dataclass
class DeploymentSnapshot:
    active: APP_STATE
    idle: APP_STATE
    version: str
    timestamp: int
    image_digest: str
    container_id: str
    container_name: str
    container_image: str
    container_tags: str

    @classmethod
    def minimal(
        cls,
        active: APP_STATE,
        idle: APP_STATE,
        *,
        version: str = "",
        timestamp: int = 0,
    ) -> "DeploymentSnapshot":
        """Snapshot with only routing slots filled; use when full metadata is unknown."""
        return cls(
            active=active,
            idle=idle,
            version=version,
            timestamp=timestamp,
            image_digest="",
            container_id="",
            container_name="",
            container_image="",
            container_tags="",
        )


class DeploymentState:
    """
     Stores deployment state to Redis.
     This allows us to track the state of the deployment and rollback to a previous version if needed.
    """

    def __init__(self, app_name:str = "demo-app"):
        self.app_name = app_name
        self.redis_client = self._get_redis_client()


    def _get_redis_client(self)->redis.Redis | None:
        """Get Redis Client"""
        try:
            docker_client = DockerClient()
            redis_host = docker_client.get("redis").attrs["NetworkSettings"]["Networks"]["warden-network"]["IPAddress"]
            redis_port = docker_client.get("redis").attrs["NetworkSettings"]["Ports"]["6379/tcp"][0]["HostPort"]
            redis_db = int(os.getenv("REDIS_DB", 0))
            redis_url = f"redis://{redis_host}:{redis_port}"
            
            logger.info(f"Redis URL: {redis_url}")
            return redis.Redis(host=redis_host,port=redis_port, db=redis_db)
        except Exception as e:
          return None

    def _get_redis_key(self, key:str):
        """Get Redis Key"""
        return f"{self.app_name}:{key}"

    def _get_redis_value(self, key:str):
        """Get Redis Value"""
        return self.redis_client.get(self._get_redis_key(key))

    def _decode(self, value: bytes | str | None) -> str | None:
        if value is None:
            return None
        if isinstance(value, bytes):
            return value.decode("utf-8")
        return str(value)

    def _require_redis(self) -> redis.Redis:
        if self.redis_client and self.redis_client.ping():
            return self.redis_client
        logger.error("Redis client is not connected")
        raise Exception("Redis client is not connected")
    
    def get_redis_client(self)->redis.Redis:
        """Get Redis Client for use in other classes"""
        return self._get_redis_client()

    def set_snapshot(self, snapshot: DeploymentSnapshot):
        """Persist a full deployment snapshot and mark it as active."""
        client = self._require_redis()
        payload = json.dumps(asdict(snapshot))
        client.set(self._get_redis_key(f"snapshot:{snapshot.active}"), payload)
        client.set(self._get_redis_key("active"), snapshot.active)
        client.set(self._get_redis_key("active_snapshot"), payload)

    def get_snapshot(self, color: APP_STATE) -> DeploymentSnapshot | None:
        """Get deployment snapshot for a specific color."""
        client = self._require_redis()
        raw = client.get(self._get_redis_key(f"snapshot:{color}"))
        if not raw:
            return None
        data = json.loads(self._decode(raw))
        return DeploymentSnapshot(**data)

    def get_active_snapshot(self) -> DeploymentSnapshot | None:
        """Get the currently active deployment snapshot."""
        client = self._require_redis()
        raw = client.get(self._get_redis_key("active_snapshot"))
        if raw:
            data = json.loads(self._decode(raw))
            return DeploymentSnapshot(**data)

        active = self._decode(client.get(self._get_redis_key("active")))
        if not active:
            return None
        return self.get_snapshot(active)

    def get_active(self)->str:
        """
        Get active service color (blue or green).
        Snapshot remains the source of truth when available.
        """
        active_snapshot = self.get_active_snapshot()
        if active_snapshot:
            return active_snapshot.active
        client = self._require_redis()
        return self._decode(client.get(self._get_redis_key("active"))) or "blue"