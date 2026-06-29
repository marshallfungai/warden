"""
 Redis-based idempotency + lock helper for Warden
 """

import os
import uuid
import redis
import logging

from warden.docker.client import DockerClient
from warden.core.state import DeploymentState

logger = logging.getLogger(__name__)


class Coordination:
    """
    Redis-based idempotency + lock helper for Warden
     - idempotent operations
     - lock operations
     - lock expiration
     - lock release
     - lock acquisition
     - lock release
    """

    def __init__(self):
        self.deployment_state = DeploymentState()
        self.redis_client = self.deployment_state.get_redis_client()
        self.app_name = os.getenv("APP_NAME", "warden")
        self.lock_prefix = f"{self.app_name}:lock:"
        self.idempotent_prefix = f"{self.app_name}:idempotent:"

    def _decode(self, value: bytes | str | None) -> str | None:
        """Decode a value from bytes to string"""
        if value is None:
            return None
        if isinstance(value, bytes):
            return value.decode("utf-8")
        return str(value)

    def _get_lock_key(self, key:str)->str:
        """Get the lock key for a given key"""
        return f"{self.lock_prefix}{key}"
    
    def _get_idempotent_key(self, key:str)->str:
        """Get the idempotent key for a given key"""
        return f"{self.idempotent_prefix}{key}"

    def acquire_lock(self, key:str, ttl:int=30)->str|None:
        """Acquire a lock for a given key"""
        lock_id = str(uuid.uuid4())
        lock_key = self._get_lock_key(key)
        ok = self.redis_client.set(lock_key, lock_id, ex=ttl, nx=True)
        return lock_id if ok else None

    def release_lock(self, key:str, lock_id:str)->bool:
        """Release a lock for a given key"""
        lock_key = self._get_lock_key(key)
        unlock_script = """
        if redis.call("GET", KEYS[1]) == ARGV[1] then
           return redis.call("DEL", KEYS[1])
        else
            return 0
        end
        """
        return bool(self.redis_client.eval(unlock_script, 1, lock_key, lock_id))
    
    def mark_idempotent(self, key:str, ttl:int=30)->bool:
        """Mark a given key as idempotent"""
        lock_key = self._get_idempotent_key(key)
        return bool(self.redis_client.set(lock_key, "1", ex=ttl, nx=True))
    
    def is_idempotent(self, key:str)->bool:
        """Check if a given key is idempotent"""
        lock_key = self._get_idempotent_key(key)
        return bool(self._decode(self.redis_client.get(lock_key)) == "1")
    
    def is_locked(self, key:str)->bool:
        """Check if a given key is locked"""
        lock_key = self._get_lock_key(key)
        return bool(self._decode(self.redis_client.get(lock_key)) is not None)
    